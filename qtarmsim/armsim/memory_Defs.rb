module Memory_Defs
# Constantes y funciones para accesos a memoria

######################################
#Funciones basicas de acceso a memoria
# little endian (le) o big endian (be)
######################################

 #read_byte
 #---------
 #Lee un byte de la dirección dada del
 #bloque (array) de memoria
 # @param [Array] data
 # @param [Integer] dir
 # @return [Integer]
  read_byte = Proc.new {|data, dir|
    data[dir]
  }

  #read_half_le
  #------------
  #Lee media palabra (2 bytes) de la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento
  #Versión little endian
  # @param [Array] data
  # @param [Integer] dir
  # @return [Integer]
  read_half_le = Proc.new {|data, dir|
    return nil if dir & 1 == 1
    (data[dir] + (data[dir + 1] << 8)) & 0xffff
  }

  #read_half_be
  #------------
  #Lee media palabra (2 bytes) de la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento
  #Versión big endian
  # @param [Array] data
  # @param [Integer] dir
  # @return [Integer]
  read_half_be = Proc.new {|data, dir|
    return nil if dir & 1 == 1
    (data[dir + 1] + (data[dir] << 8)) & 0xffff
  }

  #read_word_le
  #------------
  #Lee una palabra (4 bytes) de la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento (solo par)
  #Versión little endian
  # @param [Array] data
  # @param [Integer] dir
  # @return [Integer]
  read_word_le = Proc.new {|data, dir|
    return nil unless dir & 1 == 0
    ((((((data[dir + 3] << 8) + data[dir + 2]) << 8) + data[dir + 1]) << 8) + data[dir]) & 0xffffffff
  }

  #read_word_be
  #------------
  #Lee una palabra (4 bytes) de la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento (solo par)
  #Versión big endian
  # @param [Array] data
  # @param [Integer] dir
  # @return [Integer]
  read_word_be = Proc.new {|data, dir|
    return nil unless dir & 1 == 0
    ((((((data[dir] << 8) + data[dir + 1]) << 8) + data[dir + 2]) << 8) + data[dir + 3]) & 0xffffffff
  }

  #write_byte
  #----------
  #Escribe un byte en la dirección dada del
  #bloque (array) de memoria
  # @param [Array] data
  # @param [Integer] dir
  # @param [Integer] byte
  write_byte = Proc.new {|data, dir, byte|
    data[dir] = byte
  }

  #write_half_le
  #-------------
  #Escribe media palabra (2 bytes) en la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento
  #Versión little endian
  # @param [Array] data
  # @param [Integer] dir
  # @param [Integer] half
  # @return [nil] en caso de error. Ver
  write_half_le = Proc.new {|data, dir, half|
    return nil if dir & 1 == 1
    data[dir] = half & 0xff
    data[dir + 1] = (half >> 8) & 0xff
  }

  #write_half_be
  #-------------
  #Escribe media palabra (2 bytes) en la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento
  #Versión big endian
  # @param [Array] data
  # @param [Integer] dir
  # @param [Integer] half
  # @return [nil] en caso de error. Ver
  write_half_be = Proc.new {|data, dir, half|
    return nil if dir & 1 == 1
    data[dir + 1] = half & 0xff
    data[dir] = (half >> 8) & 0xff
  }

  #write_word_le
  #-------------
  #Escribe una palabra (4 bytes) en la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento (solo par)
  #Versión little endian
  # @param [Array] data
  # @param [Integer] dir
  # @param [Integer] word
  # @return [nil] en caso de error. Ver
  write_word_le = Proc.new {|data, dir, word|
    return nil unless dir & 1 == 0
    data[dir] = word & 0xff
    data[dir + 1] = (word >> 8) & 0xff
    data[dir + 2] = (word >> 16) & 0xff
    data[dir + 3] = (word >> 24) & 0xff
  }

  #write_word_be
  #-------------
  #Escribe una palabra (4 bytes) en la dirección dada del
  #bloque (array) de memoria. Verifica alineamiento (solo par)
  #Versión big endian
  # @param [Array] data
  # @param [Integer] dir
  # @param [Integer] word
  # @return [nil] en caso de error. Ver
  write_word_be = Proc.new {|data, dir, word|
    return nil unless dir & 1 == 0
    data[dir + 3] = word & 0xff
    data[dir + 2] = (word >> 8) & 0xff
    data[dir + 1] = (word >> 16) & 0xff
    data[dir] = (word >> 24) & 0xff
  }

  #nothing
  #-------
  #Escrituras para ROM: nada
  # @param [Array] data
  # @param [Integer] dir
  # @param [Integer] word
  # @return [nil] en caso de error. Ver
  nothing = Proc.new {|data, dir, word|
  }

  ############################
  # Funciones basicas de reset
  # ROM o RAM
  ############################

  #ram_reset
  #---------
  #Reset para la RAM. La llena con el valor
  # predefinido
  # @param [MemoryBlock] block
  ram_reset = Proc.new {|block|
    block.fill_from_val
  }

  #rom_reset
  #---------
  #Reset para la ROM. No hace nada
  # @param [MemoryBlock] block
  rom_reset = Proc.new {|block|
  }

  # Hash de funciones de acceso básicas little endian para ram
  RAM_LE = {rb: read_byte, rh: read_half_le, rw: read_word_le,
              wb: write_byte, wh: write_half_le, ww: write_word_le, reset: ram_reset}

  # Hash de funciones de acceso básicas little endian para rom
  ROM_LE = {rb: read_byte, rh: read_half_le, rw: read_word_le,
            wb: nothing, wh: nothing, ww: nothing, reset: rom_reset}

  # Hash de funciones de acceso básicas big endian para ram
  RAM_BE = {rb: read_byte, rh: read_half_be, rw: read_word_be,
                 wb: write_byte, wh: write_half_be, ww: write_word_be, reset: ram_reset}

  # Hash de funciones de acceso básicas big endian para rom
  ROM_BE = {rb: read_byte, rh: read_half_be, rw: read_word_be,
            wb: nothing, wh: nothing, ww: nothing, reset: rom_reset}

  MEMORY_TYPES = {ram_le: RAM_LE, rom_le: ROM_LE, ram_be: RAM_BE, rom_be: ROM_BE}

  MEMORY_NAMES =  {ram_le: 'RAM', rom_le: 'ROM', ram_be: 'RAM', rom_be: 'ROM'}

end