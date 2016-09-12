require_relative 'thumbII_Defs'
require_relative 'instruction'
require_relative 'memory'

############
# Clase Core
############
# Implementa el núcleo de la arquitectura
# Quiere ser un core genérico, que se encargue de las funciones básicas y
# mantenga un estado genérico cuyos detalles concretos dependan del módulo
# de soporte de la arquitectectura.
# Básicamente se encargará de gestionar la ejecución y mantener el estado.
# Este consta, sin perder genericidad de
# registros de usuario usr_regs
# registros de sistema sys_regs
# flags flags
# memoria memory
# El estado será un Hash con estos valores, donde los usr_regs serán un array,
# los flags y los sys_regs serán hashes y la memoria será tal objeto.


class Core

  attr_reader :arch

  #initialize
  #----------
  #Reset del sistema y configuración de memoria. Indicamos la arquitectura que entiende el core
  def initialize(arch, block = nil)
    @arch = arch
    memoria = (block.nil?) ? Memory.new(0x10000000, 1024, 0, 'Data RAM') : Memory.new(block)
    #b = Memory_block.new(0x20000000, 128, 0, 'Stack')
    #b.fill_from_val
    #memoria.add_block(b)
    #b = Memory_block.new(0, 1024, 0, 'ROM')
    #b.fill_random
    #memoria.add_block(b)
    @estado = ThumbII_Defs.reset
    @estado[:memory] = memoria
  end

  #execute
  #-------
  #Ejecuta la instrucción que se pasa como parámetro y actualiza el
  #estado del core. Devuelve los valores modificados
  #Revisar cómo se modifica el PC
  # @param [Instruction] inst
  # @return [Hash]
  def execute(inst)
    #p inst
    #p inst.operands
    res = inst.execute(@estado)
    #puts "Salida :"
    #p res
    if res[:usr_regs].nil?
      res[:usr_regs] = [ThumbII_Defs::PC, @estado[:usr_regs][ThumbII_Defs::PC] + 2 * inst.size]
    else
      haypc = false
      it = res[:usr_regs].length / 2 - 1
      0.upto(it) do |idx|
        haypc = true if res[:usr_regs][2 * idx] == ThumbII_Defs::PC
      end
      if haypc == false
        res[:usr_regs] << ThumbII_Defs::PC
        res[:usr_regs] << @estado[:usr_regs][ThumbII_Defs::PC] + 2 * inst.size
      end
    end
    res = update res
    return res
  end

  #update
  #-------
  #Actualiza el estado del core añadiendo los valores del hash que se pasa como
  #parámetro.
  # @param [Hash] data
  def update(data)
    #p @estado
    if data[:usr_regs] != nil
      numit = data[:usr_regs].length / 2
      0.upto(numit - 1) do |ind|
        @estado[:usr_regs][data[:usr_regs][2 * ind]] = data[:usr_regs][2 * ind + 1] & 0xFFFFFFFF
      end
    end
    if data[:flags] != nil
      data[:flags].keys.each do |key|
        @estado[:flags][key] = data[:flags][key]
      end
    end
    if data[:memory] != nil
      idx = 0
      data[:memory][1].each do |par|
        acok = @estado[:memory].access(data[:memory][0], par[0], par[1])
        if acok.is_a?(Symbol)
          data[:error] = [acok, par[0]]
          if idx == 0
            data.delete(:memory)
          else
            data[:memory][1] = data[:memory][1][0..idx - 1]
          end
          break
        end
        idx += 1
      end
    end
  return data
  end

  #memory
  #------
  #Podría ser un accessor, pero como la memoria está oculta en el estado lo
  #hacemos así
  # @return [Memory]
  def memory
    @estado[:memory]
  end

  #reg
  #---
  #Devuelve el valor del registro de la arquitectura cuyo número se indica
  # @param [Integer] num
  # @return [Integer]
  def reg(num)
    @estado[:usr_regs][num]
  end

  #flag
  #----
  #Devuelve el valor del flag de la arquitectura cuyo nombre se indica
  # @param [Symbol] sym
  # @return [Integer]
  def flag(sym)
    @estado[:flags][sym]
  end

  #flags
  #-----
  #Devuelve un hash con los flags de la arquitectura
  # @param [Symbol] sym
  # @return [Integer]
  def flags
    @estado[:flags]
  end

  #memory_xxxx
  #-----------
  #Funciones para acceder a datos de memoria a efectos de IU sobre todo.
  #Se utilizan los tres tamaños estándar, 8, 16 y 32 bytes.
  #El único parámetro es la dirección a acceder.
  #memory_byte
  def memory_byte(dir)
    memory.access(:rb, dir, nil)
  end

  #memory_half
  def memory_half(dir)
    memory.access(:rh, dir, nil)
  end

  #memory_word
  def memory_word(dir)
    memory.access(:rw, dir, nil)
  end
end