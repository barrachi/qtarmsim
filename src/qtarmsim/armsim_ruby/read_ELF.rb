#-*- coding: utf-8 -*-
require_relative 'memory_Defs'
require_relative 'memory_block'


ACESSES = Memory_Defs::RAM_LE_NA
ELFCLASS = ['Invalid object', '32 bit object', '64 bit object']
ELFDATA = ['Invalid data', 'LSB data', 'MSB data']
ELFVERSION = ['Invalid version', 'Current version']
ELFTYPE = ['Invalid type', 'Object file', 'Executable file', 'Shared object file']
ELFSECTYPES = ['Inactiva', 'Definida por el programa', 'Tabla de simbolos', 'Tabla de strings', 'Tabla de reubicacion con datos',
              'Tabla hash de simbolos', 'Informacion para el enlazado dinamico', 'Notas', 'No bits', 'Tabla de reubicacion',
              'Reservado', 'Tabla de simbolos dinamicos']
ELFSYMBIND = ['Local', 'Global', 'Weak']
ELFSYMTYPE = ['No type', 'Data object', 'Function or code', 'Section', 'File']
STT_FUNC = 2
SHN_COMMON = 65522
SHN_NAME  = 65521
ORIG_CODE = 0x00180000
ORIG_DATA = 0x20070000
END_DATA =  0x20070800
ORIG_EXTERN = 0x00004000
SIZE_EXTERN = 16

BLOCK0 = [0x30, 0xBF]

#Struct para la lectura de la cabezera de sección. Los tamaños de los campos se ven en la función
#get_section_hdr de ELF File
SecHeader = Struct.new(:name, :type, :flags, :addr, :offset, :size, :link, :info, :addralign, :entsize)
#Struct para la lectura de entradas de la tabla de símbolos. Los tamaños de los campos se ven en la función
#get_symbol_entry de ELF File. El tamaño de una entrada es SYMSIZE
SymTab = Struct.new(:name, :value, :size, :info, :other, :shndx)
SYMSIZE = 16
#Struct para la lectura de entradas de la tabla de rubicacion. Los tamaños de los campos se ven en la función
#get_relocation_entry de ELF File. El tamaño de una entrada es RELSIZE
RelTab = Struct.new(:offset, :info)
RELSIZE = 8

#Creamos la clase Section para gestionar mejor sus acciones,
#pero los datos vienen del fichero, obviamente
class Section
  attr_accessor :idx
  attr_accessor :header
  attr_accessor :data
  attr_accessor :name

  def to_s
    res = 'Seccion %d: ' % @idx
    res += @name.nil? ? 'Nombre no disponible' : @name
    res += " [%d]\n" % @header[:name]
    res += '  Tipo: ' + (@header[:type] < 11 ? ELFSECTYPES[@header[:type]] : " [%08X]" % @header[:type])
    res += @header[:entsize] == 0 ? "\n" : ", %d bytes por entrada\n" % @header[:entsize]
    res += "  Tamano: %d - Offset: %d - Direccion: %X - Alineamiento: %d\n" % [@header[:size], @header[:offset], @header[:addr], @header[:addralign]]
    res += '  Atributos: '
    if (flags = @header[:flags]) == 0
      res += "ninguno\n"
    else
      res += 'modificable ' unless (flags & 1) == 0
      res += 'mapeada ' unless (flags & 2) == 0
      res += 'ejecutable ' unless (flags & 4) == 0
      res += 'especificos de la arquitectura ' unless (flags & 0xF0000000) == 0
      res += "\n"
    end
    res += case @header[:type]
             when 2, 11 then "  Tabla de strings: %d - Ultimo simbolo local: %d\n" % [@header[:link], @header[:info]]
             when 4, 9 then "  Tabla de simbolos: %d - Reubica la seccion: %d\n" % [@header[:link], @header[:info]]
             when 5 then "  Tabla de simbolos: %d\n" % @header[:link]
             when 6 then "  Tabla de strings: %d\n" % @header[:link]
             else ''
           end
    return res
  end
end

#Creamos la clase SymbolTableEntry para gestionar mejor sus acciones,
#pero los datos vienen del fichero, obviamente
class SymbolTableEntry
  attr_accessor :idx
  attr_accessor :data
  attr_accessor :name

  def to_s
    res = 'Simbolo %d: ' % @idx
    res += @name.nil? ? 'Nombre no disponible' : @name
    res += " [%d]\n" % @data[:name]
    sec = @data[:shndx]
    res += "  %s: %d - Tamano: %d - Seccion: %s\n" % [sec == SHN_COMMON ? 'Align' : 'Offset', @data[:value], @data[:size], sec == SHN_COMMON ? 'COMMON' : sec.to_s]
    bind = (@data[:info] >> 4) & 0x0F
    tipo = @data[:info] & 0x0F
    res += "  Tipo: %s - Ambito: %s\n" % [(tipo < 5 ? ELFSYMTYPE[tipo] : 'Definido por la arquitectura'), (bind < 3 ? ELFSYMBIND[bind] : 'Definido por la arquitectura')]
    return res
  end
end

#Creamos la clase RelocationEntry para gestionar mejor sus acciones,
#pero los datos vienen del fichero, obviamente
class RelocationEntry
  attr_accessor :idx
  attr_accessor :data

  def to_s
    res = 'Reubicacion %d: ' % @idx
    res += "Simbolo: %d - Tipo: %d - Offset: %d\n" % [@data[:info] >> 8, @data[:info] & 0xFF , @data[:offset]]
    return res
  end
end

class ELF_File < File

  attr_accessor :sections           #Array de secciones
  attr_accessor :symbols            #Array de símbolos
  attr_accessor :relocations        #Array de arrays de entradas de reubicación
  attr_accessor :section_names_idx  #Indice de la tabla de strings de nombres de seccion
  attr_accessor :string_table_idx   #Indice de la tabla de strings
  attr_accessor :sym_table_idx      #Indice de la tabla de símbolos
  attr_accessor :rel_idx            #Array de indices de las tablas de reubicacion
  attr_accessor :wks                #well known sections. Aquí ponemos las secciones concidas con nombre, en un hash
  attr_accessor :wks_orig           #Inicios de la secciones. text y data fijos, rodata y bss calculados
  attr_accessor :externSymbols

  def initialize(*)
    @rel_idx = Array.new
    @relocations = Array.new
    @wks = {'.text' => 0, '.rodata' => 0, '.data' => 0, '.bss' => 0}  # ¿habrá más?
    @wks_orig = {'.text' => ORIG_CODE, '.rodata' => 0, '.data' => ORIG_DATA, '.bss' => 0}
    super
  end

  #get_array
  #---------
  #Leemos n bytes del fichero y los ponemos en un array
  #@param [Integer] n
  #@return [Array]
  def get_array(n)
    res = Array.new
    1.upto(n) do
      res << getbyte
    end
    return res
  end

  #get_half
  #--------
  #Leemos un entero de 16 bits del fichero
  #@return [Integer] 16 bits
  def get_half
    res = getbyte + getbyte * 256
  end

  #get_word
  #--------
  #Leemos un entero de 32 bits del fichero
  #@return [Integer] 32 bits
  def get_word
    res = getbyte + 256 * ( getbyte + 256 * ( getbyte + 256 * getbyte ))
  end

  #get_section_hdr
  #---------------
  #Leemos una entrada de la tabla de cabeceras de sección
  #@return [SecHeader]
  def get_section_hdr
    res = SecHeader.new
    0.upto(res.length - 1) do |idx|
      res[idx] = get_word
    end
    return res
  end

  #get_symbol_entry
  #----------------
  #Leemos una entrada de la tabla de símbolos
  #@return [SymTab]
  def get_symbol_entry
    res = SymTab.new
    0.upto(2) do |idx|
      res[idx] = get_word
    end
    res[3] = getbyte
    res[4] = getbyte
    res[5] = get_half
    return res
  end

  #get_relocation_entry
  #--------------------
  #Leemos una entrada de la tabla de reubicacion
  #@return [RelTab]
  def get_relocation_entry
    res = RelTab.new
    0.upto(1) do |idx|
      res[idx] = get_word
    end
    return res
  end

  #read_section
  #------------
  #Leemos los datos de una sección en un array de bytes
  #@param [Integer] number
  #@return [Array]
  def read_section(number)
    res = Array.new
    offset = @sections[number].header[:offset]
    size = @sections[number].header[:size]
    seek(offset, IO::SEEK_SET)
    1.upto(size) do
      res << getbyte
    end
    return res
  end

  #fill_section
  #------------
  #Leemos los datos de una sección en un array de bytes
  #@param [Integer] number
  #@return [Array]
  def fill_section(number)
    @sections[number].data = read_section(number)
  end

  #section_names_data
  #------------------
  #Devuelve la tabla de nombres de seccion
  #@return [Array]
  def section_names_data
    @sections[@section_names_idx].data
  end

  #string_table_data
  #-----------------
  #Devuelve la tabla de strings
  #@return [Array]
  def string_table_data
    @sections[@string_table_idx].data
  end

  #fill_string_table_data
  #----------------------
  #Leemos los datos dla tabla de strings
  def fill_string_table_data
    fill_section(@string_table_idx)
  end

  #fill_section_names_data
  #-----------------------
  #Leemos los datos dla tabla de strings de nombres de seccion
  def fill_section_names_data
    fill_section(@section_names_idx)
  end

  #fill_relocation_table_data
  #--------------------------
  #Leemos los datos de la tabla de reubicacion con indice dado
  def fill_relocation_table_data(idx)
    fill_section(@rel_idx[idx])
  end

  #get_string
  #----------
  #Leemos un string de los datos de una sección a partir de un índice
  #@param [Integer] number
  #@param [Integer] idx
  #@return [String]
  def get_string(number, idx)
    res = ''
    while(@sections[number].data[idx] != 0) do
      res += @sections[number].data[idx].chr
      idx += 1
    end
    return res
  end

  #get_string_table_string
  #-----------------------
  #Leemos un string de la tabla de strings partir de un índice
  #@param [Integer] idx
  #@return [String]
  def get_string_table_string(idx)
    get_string(@string_table_idx, idx)
  end

  #get_section_name_string
  #-----------------------
  #Leemos un string de la tabla de nombres de sección partir de un índice
  #@param [Integer] idx
  #@return [String]
  def get_section_name_string(idx)
    get_string(@section_names_idx, idx)
  end

  #Aplicamos la relocalización. Acabamos con un bloque de
  #datos y otro de codigo y la tabla de símbolos en memoria.
  def relocate
    $warn = Array.new
    symbolTable = Hash.new
    #
    bindTable = Hash.new
    code =  @sections[@wks['.text']].data.nil? ? BLOCK0 : @sections[@wks['.text']].data.dup
    data = @sections[@wks['.data']].data.nil? ? [0, 0, 0, 0] : @sections[@wks['.data']].data.dup
    bssdir = @wks_orig['.bss']
    externdir = ORIG_EXTERN
    @symbols.each do |symbol|
      symsection = symbol.data[:shndx]
      bind = (symbol.data[:info] >> 4) & 0x0F
     # if bind == 1
     if (bind == 1) && (symsection == 0)
        if @externSymbols.nil? || @externSymbols[symbol.name].nil?
          $warn << "Símbolo «%s» no definido." % symbol.name
        end
      end
      next if symsection == SHN_NAME
      #Si no tiene nombre lo bautizamos con sección:número de símbolo
      symname = (symbol.name.length == 0) ? "SEC%d:S%d" % [symsection, symbol.idx]: symbol.name
      #Lo buscamos en la tabla
      if symsection == SHN_COMMON
        #En el BSS lo hemos de alinear y crear espacio
        if bssdir % symbol.data[:value] != 0
          bssdir += symbol.data[:value] - (bssdir % symbol.data[:value])
        end
        symaddress = bssdir
        bssdir += symbol.data[:size]
      elsif symsection == 0
        #Esto lo arreglaría el linker, nosotros vemos si el simbolo está en los del firmware o usamos un contador de externos que crece en pasos de SIZE_EXTERN
        if @externSymbols.nil? || (firmaddress = @externSymbols[symname]).nil?
          symaddress = externdir
          externdir += SIZE_EXTERN
        else
          symaddress = firmaddress
        end
      else
        symaddress = @wks_orig[@sections[symsection].name]
        symaddress += symbol.data[:value] unless symaddress.nil?
      end
      if !symaddress.nil?
        symaddress = symaddress & 0xFFFFFFFE if symbol.data[:info] & 0x0F == STT_FUNC
        symbolTable[symname] = symaddress
        bindTable[symname] = bind
      end
    end
    @relocations.each_with_index do |rel, idx|
      dest = ( @sections[rel_idx[idx]].header[:info] == @wks['.text'] ) ? code : data
      basedir = ( @sections[rel_idx[idx]].header[:info] == @wks['.text'] ) ? @wks_orig['.text'] : @wks_orig['.data']
      orig = @sections[@sections[rel_idx[idx]].header[:info]].data
      if @sections[rel_idx[idx]].header[:link] != @sym_table_idx
        puts "ERROR: tabla de simbolos referida (%d) distinta de la global (%d)" % [@sections[rel_idx[idx]].header[:link], @sym_table_idx]
        return nil
      end
      rel.each do |entry|
        symbol = @symbols[entry.data[:info] >> 8]
        symsection = symbol.data[:shndx]
        #Si no tiene nombre lo bautizamos con sección:número de símbolo
        symname = (symbol.name.length == 0) ? "SEC%d:S%d" % [symsection, symbol.idx]: symbol.name
        symaddress = symbolTable[symname]
        #Vamos a calcular y aplicar las reubicaciones
        #S es la dirección final del símbolo, symaddress
        #A es el addend, es decir el contenido en el fichero de la dirección a reubicar -porque son rel y no rela
        #P es la dirección de la posición a reubicar, es decir la dirección base de la sección más es offset
        offset = entry.data[:offset]
        poffset = basedir + offset
        type = entry.data[:info] & 0xFF
        addend = ACESSES[:rw].call(orig, offset)
        # Mejor en array. De momento ponemos los tipos 2 y 10 que son los que salen
        case type
          when 2
            result = addend + symaddress
          when 10
            p "addend: %08X" % addend
            #immediate = ((addend & 0x7FF) << 1) + (addend & 0x7FF0000) >> 4
            immediate = ((addend & 0x7FF) << 12) + ((addend & 0x7FF0000) >> 15)
            immediate = immediate | 0xFF800000 unless (immediate & 0x400000 ) == 0
            p "Immediate: %08X" % immediate
            result = ((immediate + (symaddress - poffset)) & 0xFFFFFFFF) >> 1
            #result = (addend & 0xF800F800) | (result & 0x7FF) | ((result << 5) & 0x7FF0000)
            result = (addend & 0xF800F800) | ((result & 0x7FF) << 16) | ((result  & 0x3FF800) >> 11)
            p "result: %08X" % result
          when 102
            p "addend: %08X" % addend
            p "symaddress: %08X" % symaddress
            p "offset: %08X" % poffset
            #result = addend + (((symaddress - poffset) & 0xFFE) >> 1)
            result = addend + ((symaddress - poffset) >> 1)
            p "result: %08X" % result
          when 103
            p "addend: %08X" % addend
            p "symaddress: %08X" % symaddress
            p "offset: %08X" % poffset
            #result = addend + (((symaddress - poffset) & 0x1FE) >> 1)
            result = addend + ((symaddress - poffset) >> 1)
            p "result: %08X" % result
          else
            result = addend
        end
        ACESSES[:ww].call(dest, offset, result)
      end
    end
    #Completamos los dos arrays
    code += @sections[@wks['.rodata']].data unless @sections[@wks['.rodata']].data.nil?
    dataend = bssdir > END_DATA ? bssdir : END_DATA
    data += [0] * (dataend - @wks_orig['.bss'] + 1)
    #creamos los dos bloques y los devolvemos en un array
    bcode = Memory_block.new(@wks_orig['.text'],0, :rom_le, 0, 'ROM').fill_from_array(code)
    bdata = Memory_block.new(@wks_orig['.data'],0, :ram_le, 0, 'RAM').fill_from_array(data)
    p symbolTable
    p bcode
    p bdata
    return [bcode, bdata, symbolTable, bindTable]
  end

end

