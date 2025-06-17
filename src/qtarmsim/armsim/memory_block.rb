require_relative 'memory_Defs'

####################
# Clase Memory_block
####################
# Implementa los bloques de memoria del sistema.
# Quiere ser una simulación de dispositivos físicos -RAM, ROM, E/S...
# Puede permitir hasta simular una memoria caché, por ejemplo...
# Cada bloque es un conjunto contiguo de direcciones, con sus propios métodos
# de acceso. Se ha preferido dejar los métodos de acceso como procesos, en
# vez de hacer subclases, para dar más flexibilidad para añadirlos.

class Memory_block

  # Así podemos ordenarlos fácilmente
  include Comparable

  # Fijamos la granularidad para todos los bloques. Revisar tal vez
  ALIGN = 64

  # Cada bloque viene dado por su origen y su tamaño. Tenemos además un Hash con los métodos de acceso
  # y una descripción del bloque
  attr_reader :origen
  attr_reader :tam
  attr_reader :accesses
  attr_accessor :desc

  #initialize
  #----------
  #Funición para configurar el bloque creado, asignando en general origen, tamaño, valor de relleno y descripción.
  #Los dos primeros se ajustan a la granularidad dada. El valor de momento se deja como tal. Se llama a la función
  #set_accesses que asigna el conjunto de funciones de acceso por defecto.
  # @param [Integer/Memory_block] orig
  # @param [Integer] tam
  # @param [Integer] val
  # @param [String] desc
  def initialize(orig = 0, tam = 1024, tipo = :ram_le, val = 0, desc = '')
    @origen = orig - orig % ALIGN
    @tam = tam - tam % ALIGN
    @val = val
    @desc = desc
    @tipo = tipo
    @accesses = Hash.new
    set_accesses(tipo)
  end

  #to_s
  #----
  #Nos una cadena con los datos del bloque: su inicio, final y descripción.
  # @return [String]
  def to_s
    Memory_Defs::MEMORY_NAMES[@tipo] + ": 0x%08X - 0x%08X # " % [@origen, @origen + @tam - 1] + @desc
  end

  #<=>
  #---
  #Función de comparación. Devuelve menor (-1) si un bloque está totalmente en direcciones
  #inferiores que otro; igual (0) si intersectan y mayor (1) si está totalmente en direcciones
  #superiores
  def <=>(block)
    return -1 if block.origen >= @origen + @tam
    return 1 if @origen >= block.origen + block.tam
    return 0
  end

  #cmp
  #---
  #Función de comparación con una dirección. Devuelve menor (-1) si es inferior,
  #igual (0) si está contenida en el bloque y mayor (1) si es superior
  # @param [Integer] address
  # @return [Integer]
  def cmp(address)
    return -1 if address < @origen
    return 1 if address >= @origen + @tam
    return 0
  end

  #access
  #------
  #Invoca la función que tiene asociada al acceso
  #según el tipo
  # @param [Symbol] type
  # @param [Integer] dir
  # @param [Integer] val
  def access(type, dir, val)
    @accesses[type].call(@data, dir, val)
  end

  #fill_from_file
  #--------------
  #Genera los datos del bloque de memoria desde un fichero, copiando
  #byte a byte. Ajusta el tamaño, que aumenta hasta estar alineado
  #(rellena con 0)
  # @param [String] filename
  # @return [Memory_block]
  def fill_from_file(filename)
    b = Array.new
    t = 0
    File.open(filename, 'r') do |file|
      file.each_byte do |ch|
        b << ch
        t += 1
      end
    end
    @data = b
    rm = t % ALIGN
    @tam = rm == 0 ? t : t + ALIGN - rm
    b.length.upto(@tam - 1) do
      @data << 0
    end
    return self
  end

  #fill_from_array
  #---------------
  #Genera los datos del bloque de memoria desde un array
  #byte a byte. Ajusta el tamaño
  #(rellena con 0)
  # @param [Array] input
  # @return [Memory_block]
  def fill_from_array(input)
    @data = input.dup
    t = @data.length
    rm = t % ALIGN
    @tam = rm == 0 ? t : t + ALIGN - rm
    t.upto(@tam - 1) do
      @data << 0
    end
    return self
  end

  #fill_random
  #-----------
  #Genera los datos del bloque de memoria con bytes aleatorios
  # @return [Memory_block]
  def fill_random
    b = Array.new
    1.upto(@tam) do
      b << rand(256)
    end
    @data = b
    return self
  end

  #fill_from_val
  #-------------
  #Genera los datos del bloque de memoria con un valor constante.
  # @param [Integer] val
  # @return [Memory_block]
  def fill_from_val(val = @val)
    @data = Array.new(@tam, val)
    return self
  end

  #set_accesses
  #-------------
  #Modifica la lista de funciones de acceso según la lista que se pasa,
  #creando accesos nuevos o modificando los existentes
  # @param [Symbol] tipo
  def set_accesses(tipo)
    list = Memory_Defs::MEMORY_TYPES[tipo]
    list.keys.each do |key|
      @accesses[key] = list[key]
    end
  end

  #reset
  #-----
  #De momento pone a 0
  def reset
    @accesses[:reset].call(self)
  end
end