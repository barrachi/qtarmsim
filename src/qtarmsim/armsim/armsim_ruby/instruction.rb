require_relative 'thumbII_Defs'

###################
# Clase Instruction
###################
# Implementa un formato intermedio de instrucción que, además de mantener el opcode,
# mantiene el tipo -único y codificado en un símbolo- y una lista de operandos.
# Pretende ser independiente de arquitectura, basándose en un módulo que la soporta.

class Instruction

  # La instrucción guarda el opcode, un identificador único del tipo y la lista de operandos
  # tal y como se encuentran en la instrucción -vamos, según los modos de direccionamiento
  attr_accessor :words
  attr_reader :size
  attr_accessor :operands

  #initialize
  #----------
  #Función para iniciar la instrucción, que almacena el opcode.
  # @param [Array] word
  def initialize(words, dir)
    @words = words
    @address = dir
  end

  #Modificamos los accesors de type para que lo lea de forma normal,
  #pero al escribirlo se modifique la lista de instrucciones y el tamaño
  def type
    @type
  end

  def type=(it)
    @type = it
    @size = ThumbII_Defs::SET[@type][4]
    if @size == 1
      @words = @words[0]
    else
      @words = @words[0..size-1]
    end
  end

  #to_s
  #----
  #Formatea en bonito la instrucción, siguiendo las normas del ensamblador de la arquitectura
  # @return [String]
  def to_s
    ThumbII_Defs.to_s(@type, @operands, @address)
  end

  #kind
  #----
  #Devuelve el tipo de operación, más general
  #que type
  def kind
    ThumbII_Defs::SET[@type][1]
  end

  #execute
  #-------
  #Función para ejecutar la instrucción. EL core la invoca para cada
  #instrucción pasándole su estado. Devuelve las partes del estado a modificar.
  #Se basa en dos funciones del módulo que soporta la arquitectura, una que prepara la
  #lista de operandos en función de la instrucción y el estado, y otra que ejecuta con
  #esos operandos y devuelve el estado a modificar en el core.
  # @param [Hash] estado
  # @return [Hash]
  def execute(estado)
    data = ThumbII_Defs.prep_data(@type, @operands, estado)
    #puts "Data: "
    #p data
    ThumbII_Defs.execute(@type, data)
  end
end