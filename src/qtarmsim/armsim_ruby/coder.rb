require_relative 'thumbII_Defs'
require_relative 'instruction'

#############
# Clase Coder
#############
# Implementa los mecanismos de decodificación y codificación de instrucciones
# Se pretende que sea una clase genérica, que codifique y decodifique
# utilizando funciones de un módulo que contenga el conocimiento de la arquitectura

class Coder

  #decode
  #------
  #Decodifica un grupo de palabras y genera una instrucción, que
  #es un formato intermedio fácil de ejecutar e imprimir.
  #Se apoya en las funciones get_type y get_operands
  # @param [Array] words
  # @param [Integer] counter
  # @return [Instruction]
  def decode(words, dir = nil)
    res = Instruction.new(words, dir)
    type = get_type(words)
    type = :udef if type.nil?
    res.type = type
    res.operands = get_operands(words, type)
    return res
  end

  #get_type
  #--------
  #Decodifica una palabra y devuelve el tipo de instrucción.
  #Se apoya en las funciones y estructuras del módulo que
  #soporta la arquitectura. Recorre recursivamente las listas de
  #decodificación hasta que encuentra el tipo -devuelve nil si no.
  # @param [Array] words
  # @return [Symbol]
  def get_type(words)
    lista = ThumbII_Defs::MAINOPC
    res = 0
    size = 0
    while lista[1] != 0 do
      if (size != lista[4])
        size = lista[4]
        word = 0;
        0.upto(size - 1) do |idx|
          word = (word << 16) + words[idx]
        end
      end
      opcode = ThumbII_Defs.to_bin(ThumbII_Defs.valor_campo(word, lista[2]), lista[1])
      lista = lista[3]
      lista.each do |elemento|
        res = ThumbII_Defs.compara_bin(opcode, elemento[0])
        next if res == 1
        return nil if res == -1
        return elemento[2] if elemento[1] == 0
        lista = elemento
        break
      end
      return nil if res == 1
    end
  end

  #get_operands
  #------------
  #Dado el tipo y las palabras, devuelve el valor de los operandos.
  #Se apoya en la lista de máscaras, tipos y las funciones del módulo que
  #soporta la arquitectura.
  # @param [Array] words
  # @param [Symbol] type
  # @return [Array]
  def get_operands(words, type)
    lista = ThumbII_Defs::SET[type]
    size = lista[4]
    word = 0;
    0.upto(size - 1) do |idx|
      word = (word << 16) + words[idx]
    end
    res = Array.new()
    lista[3].each_with_index do |msc, idx|
      res << ThumbII_Defs.valor_campo(word, msc, lista[2][idx])
    end
    return res
  end

end