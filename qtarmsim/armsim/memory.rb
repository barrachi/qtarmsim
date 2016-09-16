require_relative 'memory_block'

##############
# Clase Memory
##############
# Implementa la memoria del core
# Quiere ser una unidad de gestión de accesos fuera del core
# más que una memoria.
# Por ello es simplemente un array ordenado -quiere ser un mapa de memoria-
# de bloques de memoria de la clase Memory_block. 
# Añade funciones de gestión comunes a todos los accesos, pero para realizar
# acciones específicas las redirige al bloque correspondiente a la dirección de acceso

class Memory

  attr_accessor :symbolTable

  #initialize
  #----------
  #Funición para configurar la memoria. Se asigna al tiempo el primer bloque.
  #por ello, se puede pasar solo este bloque si se ha creado aparte, o bien
  #se pueden pasar datos de un bloque de memoria -origen, tamaño, valor de relleno y descripción
  #En este segundo caso, se llama a la creación del bloque y se asigna como primero de la memoria
  # @param [Integer/Memory_block] orig
  # @param [Integer] tam
  # @param [Integer] val
  # @param [String] desc
  def initialize(orig = 0, tam = 1024, val = 0, desc = 'Main memory')
    b = orig.is_a?(Memory_block) ? orig : Memory_block.new(orig, tam, :ram_le, val, desc).fill_from_val
    @data = [b]
  end

  #to_s
  #----
  #Nos da el mapa de memoria, escribiendo para cada bloque su inicio, final y descripción (al llamar a to_s)
  # @return [String]
  def to_s
    res = ''
    @data.each do |b|
      res += b.to_s + "\r\n"
    end
    return res
  end

  #add_region
  #----------
  #Añade una nueva región de memoria, para ello crea un bloque y lo añade con add_block,
  #dejándolos ordenados por direcciones.
  #Si el bloque intersecta alguno de los existentes no lo inserta y devuelve nil
  # @param [Integer] orig
  # @param [Integer] tam
  # @param [Integer] val
  # @param [String] desc
  def add_region(orig, tam, val = 0, tipo = :ram_le, desc ='Unknown')
    b = Memory_block.new(orig, tam, tipo, val, desc)
    add_block(b)
  end

  #add_block
  #---------
  #Añade un nuevo bloque de memoria ya creado,
  #dejándolos ordenados por direcciones.
  #Si el bloque intersecta alguno de los existentes no lo inserta y devuelve nil
  # @param [Memory_block] b
  def add_block(b)
    return nil unless @data.find_index(b).nil?
    @data << b
    @data.sort!
  end

  #find_block
  #-----------
  #Devuelve el bloque de memoria a que accede una dirección dada
  #o nil si no lo hay.
  # @param [Integer] address
  # @return [Memory_block]
  def find_block(address)
    @data.each do |b|
      d = b.cmp(address)
      return b if d == 0
      return nil if d < 0
    end
    return nil
  end

  #access
  #------
  #Propaga un acceso a memoria al bloque al que se refiere.
  #Busca el bloque e invoca la función que tiene asociada al acceso
  #según el tipo. Si el bloque no existe devuelve error.
  # @param [Symbol] type
  # @param [Integer] dir
  # @param [Integer] data
  def access(type, dir, data = nil)
    b = find_block(dir)
    b.nil? ? :errnoblock : b.access(type, dir - b.origen, data)
  end

  #reset
  #------
  #Propaga el reset a todas las memorias
  def reset
    @data.each do |b|
      b.reset
    end
  end
end


