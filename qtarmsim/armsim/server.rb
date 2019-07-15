#!usr/bin/env ruby
#-*- coding: utf-8 -*-

require 'socket'
require 'shell'
require 'rbconfig'
require 'fileutils'
require_relative 'thumbII_Defs'
require_relative 'instruction'
require_relative 'coder'
require_relative 'core'
require_relative 'memory'
require_relative 'memory_block'
require_relative 'read_ELF'

FIRMWARE = 'C:/Users/fabregat/Desktop/Firmware.o'
GCC = 'C:/devkitPro/devkitARM/bin/arm-none-eabi-gcc.exe'
CL1 = '-mcpu=cortex-m1 -mthumb -c'
CL3 = '-mcpu=cortex-m3 -mthumb -c'

ORIG_CODE = 0x00180000  # Repetido en read_ELF. Ver
ORIG_DISP = 0x20080000  # Display
ORIG_FIRMWARE = 0x00190000# Firmware
SIZE_DISP = 0x400       # 1K

Errores = { orden: "Orden no reconocida\r\n",
            args:  "Argumentos erróneos\r\n",
            sistema: "Error del sistema\r\n",
            rango: "Fuera de rango\r\n",
            vacio: "No hay datos\r\n",
            noexec: "Instrución indefinida o impredecible\r\n",
            call: "No es subrutina\r\nSe ejecuta STEP\r\n",
            end: "Se intenta ejecutar al final del programa\r\n",
            breakpoint: "Se ejecuta desde dirección de breakpoint\r\nEl breakpoint se ignora\r\n",
            nomem: "Se intenta ejecutar fuera de la memoria\r\n",
            path: "El directorio no existe o no es correcto\r\n",
            exe: "El archivo no existe o no es ejecutable\r\n",
            file_s: "El archivo .s no existe\r\n",
            errnoalign: "Acceso no alineado a la dirección",
            errnoblock: "Memoria inexistente en dirección"
}

###########################################
# Funciones auxiliares
###########################################
#gen_disassemble
#---------------
#Devuelve un array con el string de instruccion
#desensamblada y la instruccion. Recibe la direccion de
#memoria de la instruccion
# @param [Integer] dir
# @return [Array] (string, instruccion)

def gen_disassemble(dir)
  res = "[0x%08X] " % dir
  sdir = dir
  word = $server.proc.memory_half(dir)
  word2 = $server.proc.memory_half(dir + 2)
  return nil if word.is_a?(Symbol) || word2.is_a?(Symbol)
  res = res + "0x%04X " % word
  inst = $server.coder.decode([word, word2], dir)
  dir = dir + 2 if inst.size == 2
  res = res + "0x%04X " % word2 if inst.size == 2
  if inst.kind == :und || inst.kind == :unp
    res = res + 'NOT AN INSTRUCTION'
  else
    res = res + inst.to_s
    src = $source[sdir - ORIG_CODE]
    res = res + " ; %04d " % src[1] + src[0] unless src.nil?
  end
  #res = res +  (inst.kind == :und || inst.kind == :unp ? 'NOT AN INSTRUCTION' : inst.to_s)
  return [res, inst]
end

#gen_source
#----------
#Devuelve un hash donde, para cada direccion relativa de
#memoria de codigo tiene la fuente y el numero de linea, a partir
#del .lst
# @param [String] name
# @return [Hash] (dir_rel => [source, number])
def gen_source(name)
  p name if $dev_txt
  source = Hash.new
  intext = false
  fi = File.open(name)
  fi.each do |line|
    line = line[0..-2]
    line_number = line[0, 4].to_i
    if line_number != 0
      dir_rel = line[5, 4].hex
      data = line[10, 8].lstrip.length
      text = line[19..-1].gsub(/\t/, ' ').lstrip if line.length > 19
      if intext
        if data != 0
          if text != nil
            text = text.encode('UTF-8') if $windows
            source[dir_rel] = [text, line_number]
          end
        else
          intext = false if get_section(text) > 1
        end
      else
        intext = true if get_section(text) == 1
      end
    end
  end
  fi.close
  source
end

#get_section
#-----------
#Recibe el texto de una linea de listado. Si la linea es .text u otra sección, o
#si la línea es .section .text u otra sección, devuelve el código de la sección. Si no, devuelve 0
# @param [String] line
# @return [Integer] 0 o código de seccion
def get_section(line)
  return 0 if line.nil?
  secs = %w(.text .data .bss .rodata)
  divide = line.split(' ')
  p divide if $dev_txt
  return secs.find_index(divide[1]) + 1 if divide[0] == '.section'
  idx = secs.find_index(divide[0])
  return idx.nil? ? 0 : idx + 1
end

#reg_to_flags
#------------
#Recibe un entero y genera un hash con los valores de los flags
# @param [Integer] reg
# @return [Hash] flags
def reg_to_flags(reg)
  flags = {n: 0, z: 0, c: 0, v: 0}
  flags[:n] = 1 if reg & 0x80000000 == 0x80000000
  flags[:z] = 1 if reg & 0x40000000 == 0x40000000
  flags[:c] = 1 if reg & 0x20000000 == 0x20000000
  flags[:v] = 1 if reg & 0x10000000 == 0x10000000
  return flags
end

#flags_to_reg
#------------
#Recibe un hash con los valores de los flags y devuelve un entero con el
#formato del ASR
# @param [Hash] flags
# @return [Integer] reg
def flags_to_reg(flags)
  reg = 0
  reg = reg + 0x80000000 if flags[:n] == 1
  reg = reg + 0x40000000 if flags[:z] == 1
  reg = reg + 0x20000000 if flags[:c] == 1
  reg = reg + 0x10000000 if flags[:v] == 1
  return reg
end

#show_version
#------------
#Devuelve un string con el número de versión y
#esas cosas.
# @param [Array] entrada
# @return [String]
show_version = Proc.new { |entrada|
  res = "V 1.4\r\n(c) 2014 Germán Fabregat\r\nATC - UJI\r\nEOF\r\n"
}

#show_register
#-------------
#Devuelve un string con el registro y su valor
# @param [Array] entrada
# @return [String]
show_register = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  elsif entrada[0] > 16
    res = Errores[:rango]
  elsif entrada[0] == 16
    res = "r16: 0x%08X\r\n" % flags_to_reg($server.proc.flags)
  else
    res = "r%d: 0x%08X\r\n" % [entrada[0], $server.proc.reg(entrada[0])]
  end
  res
}

#show_memory
#-----------
#Devuelve un string con una dirección y
#su valor
# @param [Array] entrada
# @return [String]
show_memory = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  else
    res = case entrada[0]
      when 'BYTE' then "0x%08X: 0x%02X\r\n" % [entrada[2], $server.proc.memory_byte(entrada[2])]
      when 'HALF' then "0x%08X: 0x%04X\r\n" % [entrada[2], $server.proc.memory_half(entrada[2])]
      when 'WORD' then "0x%08X: 0x%08X\r\n" % [entrada[2], $server.proc.memory_word(entrada[2])]
      else Errores[:args]
    end
  end
  res
}

#show_breakpoints
#----------------
#Devuelve la lista de breakpoints
# @param [Array] entrada
# @return [String]
show_breakpoints = Proc.new { |entrada|
  if !$server.breakpoints.length
    res = Errores[:vacio]
  else
    res = ""
    $server.breakpoints.each do |bkpt|
      res = res + "0x%08X\r\n" % bkpt
    end
    res = res + "EOF\r\n"
  end
  res
}

#dump_registers
#--------------
#Devuelve un string con todos los registros
#y sus valores
# @param [Array] entrada
# @return [String]
dump_registers = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  else
    res = ""
    0.upto(15) do |idx|
      res = res + "r%d: 0x%08X\r\n" % [idx, $server.proc.reg(idx)]
    end
    res = res + "r16: 0x%08X\r\n" % flags_to_reg($server.proc.flags)
    #res = res + "EOF\r\n"
  end
  res
}

#dump_memory
#-----------
#Devuelve un string con todos los registros
#y sus valores
# @param [Array] entrada
# @return [String]
dump_memory = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  else
    res = ""
    dir = entrada[0]
    0.upto(entrada[1] - 1) do
      word = $server.proc.memory_byte(dir)
      break if word.nil?
      res = res + "0x%08X: 0x%02X\r\n" % [dir, $server.proc.memory_byte(dir)]
      dir = dir + 1
    end
    res = res + "EOF\r\n"
  end
  res
}

#reset_registers
#---------------
#Hace un reset de los registros. Devuelve OK
# @param [Array] entrada
# @return [String]

reset_registers = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  else
    regs = Array.new
    nr = 0
    estado = ThumbII_Defs.reset
    estado[:usr_regs].each do |val|
      regs << nr
      regs << val
      nr = nr + 1
    end
    estado[:usr_regs] = regs
    $server.proc.update(estado)
    res = "OK\r\n"
  end
  res
}

#reset_memory
#------------
#Hace un reset de la memoria. Devuelve OK
# @param [Array] entrada
# @return [String]

reset_memory = Proc.new { |entrada|
  $server.proc.memory.reset
  res = "OK\r\n"
}

#clear_breakpoints
#-----------------
#Elimina los puntos de ruptura. Devuelve OK
# @param [Array] entrada
# @return [String]

clear_breakpoints = Proc.new { |entrada|
  $server.breakpoints.clear
  res = "OK\r\n"
}

#clear_breakpoint
#----------------
#Elimina el punto de ruptura especificado. Devuelve OK
# @param [Array] entrada
# @return [String]

clear_breakpoint = Proc.new { |entrada|
  $server.breakpoints.delete(entrada[1])
  res = "OK\r\n"
}

#set_register
#------------
#Pone un valor en el registro dado. Devuelve OK
# @param [Array] entrada
# @return [String]

set_register = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  elsif entrada[0] > 16
    res = Errores[:rango]
  elsif entrada[0] == 16
    $server.proc.update({flags: reg_to_flags(entrada[2])})
    res = "OK\r\n"
  else
    lista = {usr_regs: [entrada[0], entrada[2]]}
    $server.proc.update(lista)
    res = "OK\r\n"
  end
  res
}

#set_memory
#----------
#Pone un valor en la dirección dada. Devuelve OK
# @param [Array] entrada
# @return [String]

set_memory = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  else
    case entrada[0]
      when 'BYTE'
        $server.proc.memory.access(:wb, entrada[2], entrada[4])
        res = "OK\r\n"
      when 'HALF'
        $server.proc.memory.access(:wh, entrada[2], entrada[4])
        res = "OK\r\n"
      when 'WORD'
        $server.proc.memory.access(:ww, entrada[2], entrada[4])
        res = "OK\r\n"
      else
        res = Errores[:args]
    end
  end
  res
}

#set_breakpoint
#--------------
#Pone un punto de ruptura. Devuelve OK
# @param [Array] entrada
# @return [String]

set_breakpoint = Proc.new { |entrada|
  $server.breakpoints << entrada[1]
  $server.breakpoints.sort!
  $server.breakpoints.uniq!
  res = "OK\r\n"
}

#disassemble
#-----------
#Devuelve las lineas de desensamblado especificadas
# @param [Array] entrada
# @return [String]

disassemble = Proc.new { |entrada|
  if $server.proc.nil?
    res = Errores[:sistema]
  else
    res = ""
    proc = $server.proc
    dir = entrada[0]
    0.upto(entrada[1] - 1) do
      dos = gen_disassemble(dir)
      break if dos.nil?
      res = res + dos[0] + "\r\n"
      dir = dir + 2
      dir = dir + 2 if dos[1].size == 2
    end
    res = res + "EOF\r\n"
  end
  res
}

#execute
#-------
#Ejecuta codigo
# @param [Array] entrada
# @return [String]

execute = Proc.new { |entrada|
  if $server.proc.nil?
      res =  Errores[:sistema]
  else
    kinds_noexec = [:und, :ump]
    kinds_end = [:wfe, :wfi]
    kinds_subr = [:blx]
    regs = Array.new
    mem = Array.new

    pc = $server.proc.reg(ThumbII_Defs::PC)
    dos = gen_disassemble(pc)
    if dos.nil?
      res = "ERROR\r\n" + Errores[:nomem] + "EOF\r\n"
    else
      case entrada[0]
        when 'STEP'
          sigue = lambda {false}
        when 'SUBROUTINE'
          if kinds_subr.find_index(dos[1].kind).nil?
            sigue = lambda {false}
            terror = Errores[:call]
          end
        when 'ALL'
          sigue = lambda {true}
        else
          res = Errores[:args]
      end

      res = "ERROR\r\n" + dos[0] + "\r\n" + "ERROR MESSAGE\r\n" + Errores[:noexec] + "EOF\r\n" unless kinds_noexec.find_index(dos[1].kind).nil?
      res = "ERROR\r\n" + dos[0] + "\r\n" + "ERROR MESSAGE\r\n" + Errores[:end] + "EOF\r\n" unless kinds_end.find_index(dos[1].kind).nil?
      terror = Errores[:breakpoint] unless $server.breakpoints.find_index(pc).nil?
    end
    if res.nil?
      mod = $server.proc.execute(dos[1])
      nregs = mod[:usr_regs] != nil ? mod[:usr_regs].length / 2 : 0
      nmem = mod[:memory] != nil ? mod[:memory][1].length : 0
      nerror = mod[:error]
      if nregs > 0
        0.upto(nregs - 1) do |ind|
          r = mod[:usr_regs][2 * ind]
          regs << r
          if sigue.nil? && r == ThumbII_Defs::LR
            pcold = mod[:usr_regs][2 * ind + 1]
            sigue = lambda {pcold != pc}
          end
        end
        regs.uniq!
        regs.sort!
      end
      if nmem > 0
        bytes = case mod[:memory][0]
                  when :wb then 0
                  when :wh then 1
                  when :ww then 3
                end
        mod[:memory][1].each do |par|
          0.upto(bytes) do |idx|
            mem << par[0] + idx
          end
        end
        mem.uniq!
        mem.sort!
      end
      if nerror != nil
        sigue = lambda {false}
        terror = "%s 0x%08X\r\n" % [Errores[nerror[0]], nerror[1]]
      end
      pc = $server.proc.reg(ThumbII_Defs::PC)
      while sigue.call
       # pc = $server.proc.reg(ThumbII_Defs::PC)
        dos = gen_disassemble(pc)
        if dos.nil?
          terror = Errores[:nomem]
          break
        end
        if !kinds_noexec.find_index(dos[1].kind).nil?
          res = "ERROR\r\n"
          terror = Errores[:noexec]
          break
        end
        if !kinds_end.find_index(dos[1].kind).nil?
          res = "END OF PROGRAM\r\n"
          break
        end
        if !$server.breakpoints.find_index(pc).nil?
          res = "BREAKPOINT REACHED\r\n"
          break
        end
        mod = $server.proc.execute(dos[1])
        pc = $server.proc.reg(ThumbII_Defs::PC) #
        nregs = mod[:usr_regs] != nil ? mod[:usr_regs].length / 2 : 0
        nmem = mod[:memory] != nil ? mod[:memory][1].length : 0
        nerror = mod[:error]
        if nregs > 0
          0.upto(nregs - 1) do |ind|
            regs << mod[:usr_regs][2 * ind]
          end
          regs.uniq!
          regs.sort!
        end
        if nmem > 0
          bytes = case mod[:memory][0]
                  when :wb then 0
                  when :wh then 1
                  when :ww then 3
                end
          mod[:memory][1].each do |par|
            0.upto(bytes) do |idx|
              mem << par[0] + idx
            end
          end
          mem.uniq!
          mem.sort!
        end
        if nerror != nil
          terror = "%s 0x%08X\r\n" % [Errores[nerror[0]], nerror[1]]
          break
        end
      end
      res = (terror.nil? ? "SUCCESS\r\n" : "ERROR\r\n") if res.nil?
      res = res + dos[0] + "\r\n"
      res = res + "AFFECTED REGISTERS\r\n"
      if regs.length > 0
        regs.each do |nreg|
          res = res + "r%d: 0x%08X\r\n" % [nreg, $server.proc.reg(nreg)]
        end
      end
      res = res + "r16: 0x%08X\r\n" % flags_to_reg($server.proc.flags)
          if mem.length > 0
        res = res + "AFFECTED MEMORY\r\n"
        mem.each do |pos|
          res = res + "0x%08X: 0x%02X\r\n" % [pos, $server.proc.memory_byte(pos)]
         end
      end
      res = res + "ERROR MESSAGE\r\n" + terror unless terror.nil?
      res = res + "EOF\r\n"
    end
  end
  res
}

#config_compiler
#---------------
#Establece el camino del compilador. Devuelve OK
# @param [Array] entrada
# @return [String]

config_compiler = Proc.new { |entrada|
  $compiler = entrada[0]
  res = "OK\r\n"
}

#config_args
#-----------
#Establece los argumentos de compilacion. Devuelve OK
# @param [Array] entrada
# @return [String]

config_args = Proc.new { |entrada|
  $args = entrada[0]
  p $args if $dev_txt
  res = "OK\r\n"
}

#config_path
#-----------
#Establece el directorio de trabajo. Devuelve OK
# @param [Array] entrada
# @return [String]

config_path = Proc.new { |entrada|
  $path = entrada[0]
  res = "OK\r\n"
}

#config_labels
#-------------
#Activa o desactiva el uso de etiquetas en el desensamblado
# @param [Array] entrada
# @return [String]

config_labels = Proc.new { |entrada|
  case entrada[0]
    when 'TRUE'
      $use_symbols = true
      res = "OK\r\n"
    when 'FALSE'
      $use_symbols = false
      res = "OK\r\n"
    else
      res = Errores[:args]
  end
  res
}

#sysinfo_memory
#--------------
#Devuelve la información de la memoria.
# @param [Array] entrada
# @return [String]

sysinfo_memory = Proc.new { |entrada|
  res = $server.proc.memory.to_s + "EOF\r\n"
}


#assemble
#--------
#Ensambla y carga un fichero. To be continued
# @param [Array] entrada
# @return [String]

assemble = Proc.new { |entrada|
  nf = entrada[0].split('.')[0]
  old_dir = Dir.pwd
  Dir.chdir($path)
  fline = nf
  cline = '"' + $compiler + '"' + ' ' + $args + ' -Wa,-alcd' + ' -o ' + fline + '.o'
  #eline = '2> ' + fline + '.err'
  eline = fline + '.err'
  #lline = '> ' + fline + '.lst'
  lline = fline + '.lst'
  #$warn = nil
  puts cline + ' '  + fline + '.s ' +  ' ' + lline + ' ' + eline if $dev_txt
  #if system(cline + ' '  + fline + '.s ' +  ' ' + lline + ' ' + eline)
  if system(cline + ' '  + fline + '.s ', :out => lline, :err => eline)
    blocks = read_ELF(fline + '.o')
    procesador = Core.new(ThumbII_Defs::ARCH, blocks[0])
    procesador.memory.add_block(blocks[1])
    procesador.memory.symbolTable = blocks[2]
    disp = Memory_block.new(ORIG_DISP, SIZE_DISP, :ram_le, 32, 'Display')
    disp.fill_from_val
    procesador.memory.add_block(disp)
    #rom2 = Memory_block.new(0x21000000, SIZE_DISP, :rom_le, 0, 'Firmware')
    #rom2.fill_from_val
    procesador.memory.add_block($firmware)
    $symbol_table = blocks[2]
    dirPC = $symbol_table['main']
    dirPC = ORIG_CODE if dirPC.nil?
    procesador.update({usr_regs: [ThumbII_Defs::PC, dirPC, ThumbII_Defs::SP, END_DATA - 128]})
    $server.proc = procesador
    $source = gen_source(fline + '.lst')
    p $source if $dev_txt
    if $warn.size == 0
      res = "SUCCESS\r\n"
    else
      res = "ERROR\r\n"
      $warn.each do |line|
        res = res + line + "\r\n"
      end
      res = res + "EOF\r\n"
    end
  else
    res = "ERROR\r\n"
    File.foreach(fline + '.err') do |line|
      res = res + line[0..-2] + "\r\n"
    end
    res = res + "EOF\r\n"
  end
  #FileUtils.copy(fline + '.o ', FIRMWARE)
  File.delete(fline + '.err')
  File.delete(fline + '.lst')
  Dir.chdir(old_dir)
  res
}


#exit
#--------
#Se acaba. Devuelve OK
# @param [Array] entrada
# @return [String]

exit = Proc.new { |entrada|
  $exit = true
  res = "OK\r\n"
}

# Listas para la ejecución de órdenes. Van indexadas por orden principal.  Si no son terminales se indica con 0
# y luego viene la lista de subórdenes. Si son terminales se indica con 1 y luego viene la función a ejecutar
# y la lista de parámetros restantes. Se incluye tipo simbólico o texto si es fijo
Show = { 'VERSION' => [1, show_version, []],
         'REGISTER' => [1, show_register, [:regname]],
         'MEMORY' => [1, show_memory, [:keyword, 'AT', :address]],
         'BREAKPOINTS' => [1, show_breakpoints, []]
}

Dump = { 'REGISTERS' => [1, dump_registers, []],
         'MEMORY' => [1, dump_memory, [:address, :nbytes]]
}

Reset = { 'REGISTERS' => [1, reset_registers, []],
          'MEMORY' => [1, reset_memory, []]
}

Clear = { 'BREAKPOINTS' => [1, clear_breakpoints, []],
          'BREAKPOINT' => [1, clear_breakpoint, ['AT', :address]]
}

Set = { 'REGISTER' => [1, set_register, [:regname, 'WITH', :hexvalue]],
        'MEMORY' => [1, set_memory, [:keyword, 'AT', :address, 'WITH', :hexvalue]],
        'BREAKPOINT' => [1, set_breakpoint, ['AT', :address]]
}

Config = { 'COMPILER' => [1, config_compiler, [:exe]],
           'ARGS' => [1, config_args, [:cad]],
           'PATH' => [1, config_path, [:path]],
           'USELABELS' => [1, config_labels, [:keyword]]
}

Sysinfo = { 'MEMORY' => [1, sysinfo_memory, []]
}

Ordenes = {'SHOW' => [0, Show],
           'DUMP' => [0, Dump],
           'DISASSEMBLE' => [1, disassemble, [:address, :ninst]],
           'RESET' => [0, Reset],
           'CLEAR' => [0, Clear],
           'SET' => [0, Set],
           'SYSINFO' => [0, Sysinfo],
           'EXECUTE' => [1, execute, [:keyword]],
           'ASSEMBLE' => [1, assemble, [:file_s]],
           'CONFIG' => [0, Config],
           'EXIT' => [1, exit, []]
}

class MainServer < TCPServer

  #A través del Core procesador podemos acceder a todo
  attr_accessor :proc
  attr_reader :coder
  attr_reader :breakpoints

  #initialize
  #----------
  # Creamos el servidor y el motor de funcionamiento.
  # Recibimos el procesador como parámentro, con la memoria ya configurada
  def initialize(procesador, puerto)
    @proc = procesador
    @breakpoints = Array.new
    #El decodificador es cosa de la interfaz. Así podemos cambiar desde ella distintas características
    @coder = Coder.new
    super('0.0.0.0', puerto)
  end

  def process(request)
    tokens = request.split(' ')
    base = Ordenes
    loop do
      key = tokens[0]
      tokens = tokens[1..-1]
      linea = base[key]
      return Errores[:orden] if linea.nil?
      if linea[0] == 1
        return Errores[:args] unless tokens.length == linea[2].length || linea[2][-1] == :cad || linea[2][-1] == :exe || linea[2][-1] == :path
        args = linea[2]
        0.upto(args.length - 1) do |idx|
          if args[idx].kind_of?(String)
            return Errores[:args] unless tokens[idx] == args[idx]
            tokens[idx] = 1;
          else
            case args[idx]
              when :regname
                return Errores[:args] unless tokens[idx][0] == 'r'
                tokens[idx] = tokens[idx][1..-1].to_i
              when :hexvalue, :address
                tokens[idx] = tokens[idx].hex
              when :nbytes, :ninst
                tokens[idx] = tokens[idx].to_i
              when :file_s
                return Errores[:file_s] unless File.file?($path + tokens[idx].split('.')[0] + '.s')
              when :cad, :path, :exe
                cad = tokens[idx]
                (idx + 1).upto(tokens.length - 1) do |idx2|
                  cad = cad + ' ' + tokens[idx2]
                end
              tokens[idx] = cad
              if args[idx] == :path
                tokens[idx] = cad.gsub('\\', "/") #
                return Errores[:path] unless File.directory?(tokens[idx])
                tokens[idx] = tokens[idx] + '/' unless tokens[idx][-1] == '/' || tokens[idx][-1] == '\\'
              elsif args[idx] == :exe
                tokens[idx] = cad.gsub('\\', "/") #
                return Errores[:exe] unless File.executable?(tokens[idx])
              end
            end
          end
        end
        return linea[1].call(tokens)
      end
      base = linea[1]
    end
  end
end

def read_ELF(name, firmware = FALSE)
  ELF_File.open(name, 'rb') do |file|
    file.externSymbols = $firmTable
    file.wks_orig['.text'] = ORIG_FIRMWARE if firmware
    e_ident = file.get_array(16)
    magic = e_ident[1].chr + e_ident[2].chr + e_ident[3].chr
    puts("MAGIC: 0x%02X %s" % [e_ident[0], magic]) if $dev_txt
    puts("CLASS: %s" % ELFCLASS[e_ident[4]]) if $dev_txt
    puts("DATA:  %s" % ELFCLASS[e_ident[5]]) if $dev_txt
    puts(ELFVERSION[e_ident[6]]) if $dev_txt
    e_type = file.get_half
    puts(ELFTYPE[e_type]) if $dev_txt
    e_machine = file.get_half
    puts("MACHINE:%d (ARM)" % e_machine) if $dev_txt
    e_version = file.get_word
    puts(ELFVERSION[e_version]) if $dev_txt
    e_entry = file.get_word
    puts("Entry point address: %d" % e_entry) if $dev_txt
    e_phoff = file.get_word
    puts("Program header table offset: %d" % e_phoff) if $dev_txt
    e_shoff = file.get_word
    puts("Section header table offset: %d" % e_shoff) if $dev_txt
    e_flags = file.get_word
    p e_flags if $dev_txt
    e_ehsize = file.get_half
    puts("ELF header size: %d" % e_ehsize) if $dev_txt
    e_phentsize = file.get_half
    puts("Program header table entry size: %d" % e_phentsize) if $dev_txt
    e_phnum = file.get_half
    puts("Program header table entries: %d" % e_phnum) if $dev_txt
    e_shentsize = file.get_half
    puts("Section header table entry size: %d" % e_shentsize) if $dev_txt
    e_shnum = file.get_half
    puts("Section header table entries: %d" % e_shnum) if $dev_txt
    e_shstrndx = file.get_half
    puts("Section name string table index: %d" % e_shstrndx) if $dev_txt

    file.seek(e_shoff, IO::SEEK_SET)
    file.sections = Array.new
    st = 0
    stable = 0
    0.upto(e_shnum - 1) do |idx|
      cursec = Section.new
      cursec.idx = idx
      cursec.header = file.get_section_hdr
      file.sections << cursec
      st = idx if cursec.header[:type] == 3 && idx != e_shstrndx
      stable = idx if cursec.header[:type] == 2
      file.rel_idx << idx if cursec.header[:type] == 9
    end
    file.section_names_idx = e_shstrndx
    file.string_table_idx = st
    file.sym_table_idx = stable
    file.fill_section_names_data
    file.fill_string_table_data
    0.upto(file.rel_idx.length - 1) do |idx|
      file.fill_relocation_table_data(idx)
    end
    file.sections.each do |cursec|
      cursec.name = file.get_section_name_string(cursec.header[:name])
      file.wks[cursec.name] = cursec.idx unless file.wks[cursec.name].nil?
      puts cursec if $dev_txt
    end
    file.wks_orig['.rodata'] = file.wks_orig['.text'] + file.sections[file.wks['.text']].header[:size]
    file.wks_orig['.rodata'] += 4 - (file.wks_orig['.rodata'] % 4) unless (file.wks_orig['.rodata'] % 4) == 0
    file.wks_orig['.bss'] = file.wks_orig['.data'] + file.sections[file.wks['.data']].header[:size]
    p file.wks if $dev_txt
    p file.wks_orig if $dev_txt
    file.seek(file.sections[stable].header[:offset], IO::SEEK_SET)
    num = file.sections[stable].header[:size] / file.sections[stable].header[:entsize]
    puts "Symbol table idx: %d, entries: %d, at file offset: %d" % [stable, num, file.sections[stable].header[:offset]] if $dev_txt
    puts "File size: %d, section end: %d\n" % [file.size, file.sections[stable].header[:offset] + file.sections[stable].header[:size] - 1 ] if $dev_txt
    file.symbols = Array.new
    0.upto(num - 1) do |idx|
      cursym = SymbolTableEntry.new
      cursym.idx = idx
      cursym.data = file.get_symbol_entry
      cursym.name = file.get_string_table_string(cursym.data[:name])
      file.symbols << cursym
    end
    if $dev_txt
      file.symbols.each do |cursec|
        puts cursec
      end
    end
    file.rel_idx.each do |rel|
      file.seek(file.sections[rel].header[:offset], IO::SEEK_SET)
      num = file.sections[rel].header[:size] / file.sections[rel].header[:entsize]
      relocations = Array.new
      0.upto(num - 1) do |idx|
        cursym = RelocationEntry.new
        cursym.idx = idx
        cursym.data = file.get_relocation_entry
        relocations << cursym
        p cursym if $dev_txt
      end
      file.relocations << relocations
    end
    if $dev_txt
      file.relocations.each do |cursec|
        puts "Tabla"
        cursec.each do |entry|
          puts entry
       end
      end
    end
    # Nos preparamos. Lo primero es leer las secciones con datos
    file.fill_section(file.wks['.text']) unless file.sections[file.wks['.text']].header[:size] == 0;
    p file.sections[file.wks['.text']].data if $dev_txt
    file.fill_section(file.wks['.data']) unless file.sections[file.wks['.data']].header[:size] == 0;
    p file.sections[file.wks['.data']].data if $dev_txt
    file.fill_section(file.wks['.rodata']) unless file.sections[file.wks['.rodata']].header[:size] == 0;
    p file.sections[file.wks['.rodata']].data if $dev_txt

    return file.relocate
  end
end

class ServerApp

  #A través del Core procesador podemos acceder a todo
  #attr_reader :procesador

  #main
  #----
  #Aquí pondremos toda la inicialización y esas cosas
  #de momento una ROM random, la RAM de datos y la pila
  def main
    $dev_txt = false
    host_os = RbConfig::CONFIG['host_os']
    $windows = host_os == "linux" ? false : true
    p $windows if $dev_txt
    p host_os if $dev_txt
    lpath = File.expand_path(File.dirname($0))
    Shell.cd(lpath)
    blocks = read_ELF('Firmware.o', TRUE)
    puerto = ARGV.length == 0 ? 8070 : ARGV[0].to_i
    @procesador = Core.new(ThumbII_Defs::ARCH, blocks[0])
    @procesador.memory.add_block(blocks[1])
    @procesador.memory.symbolTable = blocks[2]
    $symbol_table = blocks[2]
    $use_symbols = false
    $gen_trace = false
    @procesador.update({usr_regs: [ThumbII_Defs::PC, ORIG_CODE, ThumbII_Defs::SP, END_DATA - 128]})
    $firmware = blocks[0]
    $firmTable = blocks[2]
    #p blocks[3]
    blocks[3].each do |key, bind|
      $firmTable.delete(key) unless bind == 1
    end
    #p $firmTable
    $server = MainServer.new(@procesador, puerto)
    $compiler = GCC
    $args = CL1
    $path = "C:\\Users\\German\\Desarrollos\\ArduinoDue\\"
    $exit = false
    session = $server.accept
    while !$exit
      request = session.gets
      if request.nil?
        session = $server.accept
      else
        puts "Request: #{request}"
        request.force_encoding("UTF-8") if $windows
        answer = $server.process(request)
        session.puts(answer)
      end
    end
    session.close
  end
end

$app = ServerApp.new.main()