module ThumbII_Defs
# Constantes diversas de la arquitectura ThumbII
  #Arquitectura
  ARCH = 'Instrucciones Thumb de 16 bits'
  #El contador del programa es el registro 15
  PC = 15
  LR = 14
  SP = 13
  APSR = 16
  #Tabla de simbolos
 # $symbol_table = nil
  #TOBE ARMv7-M
  # Conjunto de instrucciones.
  # identificador instrucción: mnemónico - identificador operación - operandos - máscaras - numero de halfs
  SET = { lslit1:   ['lsl', :lsl, [:r3, :r3, :imm5], [0x0007, 0x0038, 0x07C0], 1],
          lsrit1:   ['lsr', :lsr, [:r3, :r3, :imm5], [0x0007, 0x0038, 0x07C0], 1],
          asrit1:   ['asr', :asr, [:r3, :r3, :imm5], [0x0007, 0x0038, 0x07C0], 1],
          movit1:   ['mov', :mov, [:r3, :imm8], [0x0700, 0x00FF], 1],
          cmpit1:   ['cmp', :add, [:r3, :imm8], [0x0700, 0x00FF], 1],
          addit2:   ['add', :add, [:r3, :imm8], [0x0700, 0x00FF], 1],
          subit2:   ['sub', :add, [:r3, :imm8], [0x0700, 0x00FF], 1],
          addrt1:   ['add', :add, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          subrt1:   ['sub', :add, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          addit1:   ['add', :add, [:r3, :r3, :imm3], [0x0007, 0x0038, 0x01C0], 1],
          subit1:   ['sub', :add, [:r3, :r3, :imm3], [0x0007, 0x0038, 0x01C0], 1],
		      andrt1:   ['and', :and, [:r3, :r3], [0x0007, 0x0038], 1],
          eorrt1:   ['eor', :eor, [:r3, :r3], [0x0007, 0x0038], 1],
          lslrt1:   ['lsl', :lsl, [:r3, :r3], [0x0007, 0x0038], 1],
          lsrrt1:   ['lsr', :lsr, [:r3, :r3], [0x0007, 0x0038], 1],
          asrrt1:   ['asr', :asr, [:r3, :r3], [0x0007, 0x0038], 1],
          adcrt1:   ['adc', :add, [:r3, :r3], [0x0007, 0x0038], 1],
          sbcrt1:   ['sbc', :add, [:r3, :r3], [0x0007, 0x0038], 1],
          rorrt1:   ['ror', :ror, [:r3, :r3], [0x0007, 0x0038], 1],
          tstrt1:   ['tst', :and, [:r3, :r3], [0x0007, 0x0038], 1],
          rsbrt1:   ['rsb', :add, [:r3, :r3], [0x0007, 0x0038], 1],
          cmprt1:   ['cmp', :add, [:r3, :r3], [0x0007, 0x0038], 1],
          cmnrt1:   ['cmn', :add, [:r3, :r3], [0x0007, 0x0038], 1],
          orrrt1:   ['orr', :orr, [:r3, :r3], [0x0007, 0x0038], 1],
          mult1:    ['mul', :mul, [:r3, :r3, :r3], [0x0007, 0x0038, 0x0007], 1],
          bicrt1:   ['bic', :and, [:r3, :r3], [0x0007, 0x0038], 1],
          mvnrt1:   ['mvn', :mov, [:r3, :r3], [0x0007, 0x0038], 1],
		      addrt2:   ['add', :add, [:r4d, :r4], [0x0087, 0x0078], 1],
          unpred:   ['unp', :unp, [], [], 1],
          cmprt2:   ['cmp', :add, [:r4d, :r4], [0x0087, 0x0078], 1],
          movrt1:   ['mov', :mov, [:r4d, :r4], [0x0087, 0x0078], 1],
          bxt1:     ['bx', :bx, [:r4], [0x0078], 1],
          blxt1:    ['blx', :blx, [:r4], [0x0078], 1],
		      ldrlt1:   ['ldr', :ldr, [:r3, :label8], [0x0700, 0x00FF], 1],
		      strrt1:   ['str', :str, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          strhrt1:  ['strh', :strh, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          strbrt1:  ['strb', :strb, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          ldrsbrt1: ['ldrsb', :ldr, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          ldrrt1:   ['ldr', :ldr, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          ldrhrt1:  ['ldrh', :ldr, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          ldrbrt1:  ['ldrb', :ldr, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
          ldrshrt1: ['ldrsh', :ldr, [:r3, :r3, :r3], [0x0007, 0x0038, 0x01C0], 1],
		      strit1:   ['str', :str, [:r3, :r3, :imm5x4], [0x0007, 0x0038, 0x07C0], 1],
          ldrit1:   ['ldr', :ldr, [:r3, :r3, :imm5x4], [0x0007, 0x0038, 0x07C0], 1],
          strbit1:  ['strb', :strb, [:r3, :r3, :imm5], [0x0007, 0x0038, 0x07C0], 1],
          ldrbit1:  ['ldrb', :ldr, [:r3, :r3, :imm5], [0x0007, 0x0038, 0x07C0], 1],
		      strhit1:  ['strh', :strh, [:r3, :r3, :imm5x2], [0x0007, 0x0038, 0x07C0], 1],
          ldrhit1:  ['ldrh', :ldr, [:r3, :r3, :imm5x2], [0x0007, 0x0038, 0x07C0], 1],
          strit2:   ['str', :str, [:r3, :imm8x4], [0x0700, 0x00FF], 1],
          ldrit2:   ['ldr', :ldr, [:r3, :imm8x4], [0x0700, 0x00FF], 1],
		      adrit1:   ['adr', :adr, [:r3, :label8], [0x0700, 0x00FF], 1],
		      addspit1: ['add', :add, [:r3, :imm8x4], [0x0700, 0x00FF], 1],
		      addspit2: ['add', :add, [:imm7x4], [0x007F], 1],
          subspit1: ['sub', :add, [:imm7x4], [0x007F], 1],
          cbzt1:    ['cbz', :cbz, [:r3, :label6d], [0x0007, 0x02F8], 1],
          sxtht1:   ['sxth', :sxth, [:r3, :r3], [0x0007, 0x0038], 1],
          sxtbt1:   ['sxtb', :sxtb, [:r3, :r3], [0x0007, 0x0038], 1],
          uxtht1:   ['uxth', :uxth, [:r3, :r3], [0x0007, 0x0038], 1],
          uxtbt1:   ['uxtb', :uxtb, [:r3, :r3], [0x0007, 0x0038], 1],
          pusht1:   ['push', :push, [:rl9], [0x01FF], 1],
          cpst1:    ['cps', :cps, [:b1, :b2], [0x0010, 0x0003], 1],
          cbnzt1:   ['cbnz', :cbnz, [:r3, :label6d], [0x0007, 0x02F8], 1],
          revt1:    ['rev', :rev, [:r3, :r3], [0x0007, 0x0038], 1],
          rev16t1:  ['rev16', :rev16, [:r3, :r3], [0x0007, 0x0038], 1],
          revsht1:  ['revsh', :revsh, [:r3, :r3], [0x0007, 0x0038], 1],
          popt1:    ['pop', :pop, [:rl9], [0x01FF], 1],
          bkptt1:   ['bkpt', :bkpt, [:imm8], [0x00FF], 1],
		      stmt1:    ['stm', :stm, [:r3, :rl8], [0x0700, 0x00FF], 1],
		      ldmt1:    ['ldm', :ldm, [:r3, :rl8], [0x0700, 0x00FF], 1],
		      udef:     ['und', :und, [], [], 1],
          svct1:    ['svc', :svc, [:imm8], [0x00FF], 1],
          bt1:      ['b', :b, [:cond, :label8s], [0x0F00, 0x00FF], 1],
		      bt2:      ['b', :b, [:label11s], [0x07FF], 1],
          nopt1:    ['nop', :nop, [], [], 1],
          yieldt1:  ['yield', :yield, [], [], 1],
          wfet1:    ['wfe', :wfe, [], [], 1],
          wfit1:    ['wfi', :wfi, [], [], 1],
          sevt1:    ['sev', :sev, [], [], 1],
          itt1:     ['it', :it, [:imm4, :cond], [0x000F, 0x00F0], 1],
          blt1:     ['bl', :blx, [:labeldbl], [0x07FF2FFF], 2],
          bt4:      ['b', :b, [:labeldbl], [0x07FF2FFF], 2],
          udef32:   ['und', :und, [], [], 2],
  }

  # Instrucciones según opcode secundario. Ver GROUPS.
  # Pasan a lista como la primera, pero casi todas sin más divisiones
  # opcode - identificador instrucción
  PRINCIPAL = [ ['000xx', 0, :lslit1],
                ['001xx', 0, :lsrit1],
                ['010xx', 0, :asrit1],
                ['01100', 0, :addrt1],
                ['01101', 0, :subrt1],
                ['01110', 0, :addit1],
                ['01111', 0, :subit1],
                ['100xx', 0, :movit1],
                ['101xx', 0, :cmpit1],
                ['110xx', 0, :addit2],
                ['111xx', 0, :subit2] ]

  ALU = [ ['0000', 0, :andrt1],
          ['0001', 0, :eorrt1],
          ['0010', 0, :lslrt1],
          ['0011', 0, :lsrrt1],
          ['0100', 0, :asrrt1],
          ['0101', 0, :adcrt1],
          ['0110', 0, :sbcrt1],
          ['0111', 0, :rorrt1],
          ['1000', 0, :tstrt1],
          ['1001', 0, :rsbrt1],
          ['1010', 0, :cmprt1],
          ['1011', 0, :cmnrt1],
          ['1100', 0, :orrrt1],
          ['1101', 0, :mult1],
          ['1110', 0, :bicrt1],
          ['1111', 0, :mvnrt1] ]

  ESPECIAL = [ ['00xx', 0, :addrt2],
               ['0100', 0, :unpred],
               ['01xx', 0, :cmprt2],
               ['10xx', 0, :movrt1],
               ['110x', 0, :bxt1],
               ['111x', 0, :blxt1] ]

  LDSTRREG = [ ['000', 0, :strrt1],
               ['001', 0, :strhrt1],
               ['010', 0, :strbrt1],
               ['011', 0, :ldrsbrt1],
               ['100', 0, :ldrrt1],
               ['101', 0, :ldrhrt1],
               ['110', 0, :ldrbrt1],
               ['111', 0, :ldrshrt1] ]

  LDSTRIMM = [ ['00', 0, :strit1],
               ['01', 0, :ldrit1],
               ['10', 0, :strbit1],
               ['11', 0, :ldrbit1] ]

  LDSTRMIX = [ ['00', 0, :strhit1],
               ['01', 0, :ldrhit1],
               ['10', 0, :strit2],
               ['11', 0, :ldrit2] ]

  HINTS = [ ['00000000', 0, :nopt1],
            ['00010000', 0, :yieldt1],
            ['0001xxxx', 0, :itt1],
            ['00100000', 0, :wfet1],
            ['0010xxxx', 0, :itt1],
            ['00110000', 0, :wfit1],
            ['0011xxxx', 0, :itt1],
            ['01000000', 0, :sevt1],
            ['0100xxxx', 0, :itt1],
            ['xxxx0000', 0, :udef],
            ['xxxxxxxx', 0, :itt1] ]

  MISC = [ ['00000xx', 0, :addspit2],
           ['00001xx', 0, :subspit1],
           ['0001xxx', 0, :cbzt1],
           ['001000x', 0, :sxtht1],
           ['001001x', 0, :sxtbt1],
           ['001010x', 0, :uxtht1],
           ['001011x', 0, :uxtbt1],
           ['0011xxx', 0, :cbzt1],
           ['010xxxx', 0, :pusht1],
           ['0110011', 0, :cpst1],
           ['1001xxx', 0, :cbnzt1],
           ['101000x', 0, :revt1],
           ['101001x', 0, :rev16t1],
           ['101011x', 0, :revsht1],
           ['1011xxx', 0, :cbnzt1],
           ['110xxxx', 0, :popt1],
           ['1110xxx', 0, :bkptt1],
           ['1111xxx', 8, 0x00FF, HINTS, 1] ]

  BSVC = [ ['0xxx', 0, :bt1],
           ['10xx', 0, :bt1],
           ['110x', 0, :bt1],
           ['1110', 0, :udef32],
           ['1111', 0, :svct1] ]

  BMSC32 = [ #['1111111xxxx1010', 0, :udef],
             ['xxxxxxxxxxx10x1', 0, :bt4],
             ['xxxxxxxxxxx11x1', 0, :blt1] ]

  TH32B10 = [ ['xxxxxxxxxxx1', 15, 0x07FFF000, BMSC32, 2] ]

  # Grupos de instrucciones según opcode. División principal
  # opcode - tamaño en bits y máscara del siguiente opcode - siguiente lista de instrucciones - numero de halfs - Descripción (opcional)
  # Si tamaño en bits es 0, en vez de máscara y lista está el id. de instruccion
  GROUPS = [ ['00xxxx', 5, 0x3E00, PRINCIPAL, 1, 'Principal'],
             ['010000', 4, 0x03C0, ALU, 1, 'Alu'],
             ['010001', 4, 0x03C0, ESPECIAL, 1, 'Especial'],
             ['01001x', 0, :ldrlt1, 'LDR'],
             ['0101xx', 3, 0x0E00, LDSTRREG, 1, 'Load Store Register'],
             ['011xxx', 2, 0x1800, LDSTRIMM, 1, 'Load Store Immediate'],
             ['100xxx', 2, 0x1800, LDSTRMIX, 1, 'Load Store Mixed'],
             ['10100x', 0, :adrit1, 'ADR'],
             ['10101x', 0, :addspit1, 'ADD SP'],
             ['1011xx', 7, 0x0FE0, MISC, 1, 'Miscellaneous'],
             ['11000x', 0, :stmt1, 'STM'],
             ['11001x', 0, :ldmt1, 'LDM'],
             ['1101xx', 4, 0x0F00, BSVC, 1, 'B SVC'],
             ['11100x', 0, :bt2, 'B'],
             ['11110x', 12, 0x07FF8000, TH32B10, 2, '32 bits, bloque 10']
  ]

  #El opcode principal son los 6 msb
  #Se mantiene el formato de las listas, por regularidad
  MAINOPC = [nil, 6, 0xFC00, GROUPS, 1]

  #Otras constantes genéricas
  #Registros con nombre especial
  PRIMALIAS = 13 # El sp
  REGALIAS = %w(sp lr pc)


  #UTILES
  #############################
  #Funciones de apoyo genéricas
  #############################

  #valor_campo
  #-----------
  #Dado un entero y una máscara de 16 bits
  #devuelve el valor del campo de bits seleccionado,
  #ajustado a la derecha. Modifica los tipos con agujeros
  #en la mascara
  # @param [Integer] entero
  # @param [Integer] mascara
  # @param [Symbol] tipo
  # @return [Integer]
  def ThumbII_Defs.valor_campo(entero, mascara, tipo = :notipo)
    salida = entero & mascara
    while (mascara % 2) == 0 do
      salida = salida / 2
      mascara = mascara / 2
    end
    salida = 8 + (salida & 7) if tipo == :r4d && salida > 8
    return salida
  end

  #ajusta_campo_d
  #--------------
  #Dado el entero resultante de valor_campo y la máscara de 16 bits con un bit aislado.
  #devuelve un entero concatenando el bit suelto como msb del grupo
  # @param [Integer] entero
  # @param [Integer] mascara
  # @return [Integer]
  def ThumbII_Defs.valor_campo_d(entero, mascara)
    while (mascara % 2) == 0 do
      mascara = mascara / 2
    end
    nmasc = 0
    while (mascara % 2) == 1 do
      mascara = mascara / 2
      nmasc = 2 * nmasc + 1
    end
    nentero = entero & nmasc
    return (nentero == entero) ? entero : nentero + nmasc + 1
  end


  #to_bin
  #------
  #dado un entero y un número de bits lng
  #devuelve una cadena en binario que lo representa
  # @param [Integer] entero
  # @param [Integer] lng
  # @return [String]
  def ThumbII_Defs.to_bin(entero, lng)
    cadena = ''
    while lng > 0 do
      cadena = ((entero & 1) == 1? '1' : '0') + cadena
      lng -= 1
      entero >>= 1
    end
    return cadena
  end

  #compara_bin
  #-----------
  #dadas dos cadenas que expresan números en binario,
  #las compara y devuelve 1, 0 ó -1 según la primera
  #sea mayor, igual o menor que la segunda
  #La segunda puede incluir x que satisfacen al 0 o al 1
  #Han de ser de igual longitud, no se verifica.
  # @param [String] cad1
  # @param [String] cad2
  # @return [Integer]
  def ThumbII_Defs.compara_bin(cad1, cad2)
    cad2.each_char.with_index do |trozo, i|
      next if trozo == 'x'
      res = cad1[i] <=> trozo
      return res unless res == 0
      end
    return 0
  end

  #eval_cond
  #---------
  #Evalua (true o false) una condición en función de los 4 bits y los
  #flags, según el manual ARMv7 (pag. 209)
  #Es un apoyo a la ejecución de instrucciones
  # @param [Integer] cond
  # @param [Hash] flags
  # @return [Boolean]
  def ThumbII_Defs.eval_cond(cond, flags)
    toggle = cond & 1
    cond = (cond >> 1) & 7
    res = case cond
      when 0 then (flags[:z] == 1)
      when 1 then (flags[:c] == 1)
      when 2 then (flags[:n] == 1)
      when 3 then (flags[:v] == 1)
      when 4 then (flags[:c] == 1) && (flags[:z] == 0)
      when 5 then (flags[:n] == flags[:v])
      when 6 then (flags[:n] == flags[:v]) && (flags[:z] == 0)
      when 7 then true
          end
    res = !res if toggle == 1 && cond != 7
    return res
  end

  ###################################################
  #Funciones para la generación de código ensamblador
  ###################################################

  #Decodificacion de los bits de condición
  CONCODES = %w(eq ne cs cc mi pl vs vc hi ls ge lt gt le al al)

  #cond_to_s
  #---------
  #dado un campo que representa el código de condición
  #devuelve una cadena con la condición
  # @param [Integer] numero
  # @return [String]
  cond_to_s = Proc.new { |numero|
    CONCODES[numero]
  }

  #nreg_to_s
  #---------
  #dado un campo que representa un registro
  #devuelve una cadena con el nombre del registro
  # @param [Integer] numero
  # @return [String]
  nreg_to_s = Proc.new { |numero|
    if numero < PRIMALIAS
      'r' + numero.to_s if numero < PRIMALIAS
    else
      REGALIAS[numero - PRIMALIAS]
    end
  }

  #nregd_to_s
  #----------
  #dado un campo disjunto (1 + 3 bits) que representa un registro
  #devuelve una cadena con el nombre del registro
  # @param [Integer] numero
  # @return [String]
  nregd_to_s = Proc.new { |numero|
    numero = (numero > 7) ? 8 + (numero & 7) : numero
    nreg_to_s.call(numero)
  }

  #imm_to_s
  #--------
  #dado un inmediato devuelve una cadena que lo representa
  #precedida del carácter #
  # @param [Integer] numero
  # @return [String]
  imm_to_s = Proc.new { |numero| '#' + numero.to_s }

  #immx2_to_s
  #----------
  #dado un inmediato devuelve una cadena que lo representa
  #multiplicado por 2 precedida del carácter #
  # @param [Integer] numero
  # @return [String]
  immx2_to_s = Proc.new { |numero| '#' + (numero * 2).to_s }

  #immx4_to_s
  #----------
  #dado un inmediato devuelve una cadena que lo representa
  #multiplicado por 4 precedida del carácter #
  # @param [Integer] numero
  # @return [String]
  immx4_to_s = Proc.new { |numero| '#' + (numero * 4).to_s }

  #label_to_s
  #----------
  #De momento es immx4_to_s Revisar
  # @param [Integer] numero
  # @return [String]
  label_to_s = Proc.new { |numero| '#' + (numero * 4).to_s }

  #labeld_to_s
  #-----------
  #De momento añade PC. Revisar
  # @param [Integer] numero
  # @return [String]
  labeld_to_s = Proc.new { |numero|
    numero = (numero > 31) ? 32 + (numero & 31) : numero
    if $address != nil
      busca = $address + 4 + numero * 2
      res = $symbol_table.key(busca) if $use_symbols
    end
    res = res.nil? ? 'pc, #' + (numero * 2).to_s: res
  }

  #label8s_to_s
  #------------
  #Extiende en signo el bit 8. De momento añade PC. Revisar
  # @param [Integer] numero
  # @return [String]
  label8s_to_s = Proc.new { |numero|
    numero = (numero > 127) ? 0 - ((numero^0xFF) + 1) : numero
    if $address != nil
      busca = $address + 4 + numero * 2
      res = $symbol_table.key(busca) if $use_symbols
    end
    res = res.nil? ? 'pc, #' + (numero * 2).to_s: res
  }

  #label11s_to_s
  #-------------
  #Extiende en signo el bit 11. De momento añade PC. Revisar
  # @param [Integer] numero
  # @return [String]
  label11s_to_s = Proc.new { |numero|
    numero = (numero > 1023) ? 0 - ((numero^0x7FF) + 1) : numero
    if $address != nil
      busca = $address + 4 + numero * 2
      res = $symbol_table.key(busca) if $use_symbols
    end
    res = res.nil? ? 'pc, #' + (numero * 2).to_s: res
  }

  #labeldbl_to_s
  #-------------
  #Específica de BL de 32 bits.
  #El bit de signo S es el bit 10 del half alto, luego j1 es el bit 13
  #y j2 el 11 del half bajo. Además el half alto tiene 10 bits de inmediato con
  #con máscara 0x3FF y el bajo 11 con máscara 0x7FF.
  #Se calcula I1 = NOT(S xor J1) e igual I2 con J2, se concatena
  #S:I1:I2:Imm10:Imm11, se extiende en signo y se multiplica por 2. De momento añade PC. Revisar
  # @param [Integer] numero
  # @return [String]
  labeldbl_to_s = Proc.new { |numero|
    imm11 = numero & 0x7FF
    imm10 = (numero & 0x03FF0000) >> 5
    s = (numero & 0x04000000) == 0? 0 : 1
    j1 = (numero & 0x02000) == 0? 0 : 1
    j2 = (numero & 0x0800) == 0? 0 : 1
    i1 = (s == j1) ? 1 : 0
    i2 = (s == j2) ? 1 : 0
    imm3 = (s * 4 + i1 * 2 + i2) << 21
    imm = (imm3 & 0x0E00000) | (imm10 & 0x1FF800) | imm11
    imm = (s == 1) ? 0 - (((imm^0xEFFFFF) + 1) & 0xEFFFFF) : imm
    if $address != nil
      busca = $address + 4 + imm * 2
      res = $symbol_table.key(busca) if $use_symbols
    end
    res = res.nil? ? 'pc, #' + (imm * 2).to_s: res
  }

  #rlist9_to_s
  #-----------
  #Pasa de un bitmap de hasta 9 registros a un string
  #en que aparecen los registros de menor a mayor separados por ,
  #y los rangos por -
  #El registro 9 se marca como x para cambiarlo por lr o pc
  # @param [Integer] numero
  # @return [String]
  rlist9_to_s = Proc.new { |numero|
    cad = '{'
    estado = 0
    hay = 0
    primero = 0
    0.upto(7) do |ind|
      entrada = numero & 1
      numero = numero / 2
      if estado == 0
        if entrada == 1
          cad += ', ' if hay == 1
          cad += 'r' + ind.to_s
          primero = ind
          hay = 1
          estado = 1
        end
      else
        if entrada == 0
          cad += '-r' + (ind - 1).to_s unless ind == primero + 1
          estado = 0
        end
      end
    end
    cad += '-r7' if estado == 1 && primero < 7
    if (numero & 1) == 1
      cad += ', ' if hay == 1
      cad += 'x'
    end
    cad += '}'
  }

  #Listas de funciones de generación de parámetros
  OPTOS = {r3: nreg_to_s, r4: nreg_to_s, r4d: nreg_to_s, label8: label_to_s, label6d: labeld_to_s,
           label8s: label8s_to_s, label11s: label11s_to_s, labeldbl: labeldbl_to_s, imm5x2: immx2_to_s, imm5x4: immx4_to_s,
           imm8x4: immx4_to_s, imm3: imm_to_s, imm7x4: immx4_to_s, imm4: imm_to_s, imm5: imm_to_s,
           imm8: imm_to_s, imm11: imm_to_s, rl8: rlist9_to_s, rl9: rlist9_to_s, cond: cond_to_s}

  #Funciones de generacion de cadenas de instrucciones

  #ibonito
  #-------
  #Dado el tipo de la instrucción y la lista de operandos (enteros)
  #devuelve una lista con los operandos en forma de cadenas adaptadas
  #al lenguaje ensamblador
  # @param [Symbol] tipo
  # @param [Array] operandos
  # @return [Array]
  def  ThumbII_Defs.ibonito(tipo, operandos)
    opbonitos = Array.new
    SET[tipo][2].each.with_index do |optipo, ind|
      opbonitos << OPTOS[optipo].call(operandos[ind])
    end
    return opbonitos
  end

  #Funciones de conversión a formato ensamblador según tipo de instrucción

  #base_to_s
  #---------
  #Función básica sin tratamiento especial.
  #Concatena el opcode principal modificado con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo s o la condición si está en
  #un bloque IT
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  base_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    final = op_s.length - 1
    cad = ''
    op_s.each_with_index do |op, ind|
      cad += ' ' + op
      cad += ',' unless ind == final
    end
    SET[auto][0] + ((itcond.nil?) ? 's' : itcond) + cad
  }

  #basef_to_s
  #----------
  #Función básica sin tratamiento especial.
  #Concatena el opcode principal modificado con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  basef_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    final = op_s.length - 1
    cad = ''
    op_s.each_with_index do |op, ind|
      cad += ' ' + op
      cad += ',' unless ind == final
    end
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #nomod_to_s
  #----------
  #Función sin tratamiento especial.
  #Concatena el opcode principal con los operandos
  #separados por comas.
  #El opcode no se modifica en ningún caso
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  nomod_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    final = op_s.length - 1
    cad = ''
    op_s.each_with_index do |op, ind|
      cad += ' ' + op
      cad += ',' unless ind == final
    end
    SET[auto][0] + cad
  }

  #basenoit_to_s
  #-------------
  #Función básica sin tratamiento especial.
  #Concatena el opcode principal modificado con los operandos
  #separados por comas.
  #El opcode no se modifica. No añade s porque siempre afecta a los flags
  #No se permite en bloque IT
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  basenoit_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    final = op_s.length - 1
    cad = ''
    op_s.each_with_index do |op, ind|
      cad += ' ' + op
      cad += ',' unless ind == final
    end
    (itcond.nil?) ? SET[auto][0] + cad : 'ERROR: no permitida en bloque IT'
  }

  #lslit1_to_s
  #-----------
  #Si el tercer operando (desplazamiento) es 0 se ha de tratar
  #es un movs, en otro caso es normal
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  lslit1_to_s = Proc.new {|auto, operandos, itcond|
    if operandos[2] == 0
      op_s = ibonito(auto, operandos)
      (itcond.nil?) ? 'movs ' + op_s[0] + ', ' + op_s[1] : 'ERROR: no permitida en bloque IT'
    else
      base_to_s.call(auto, operandos, itcond)
    end
  }

  #rsbt1_to_s
  #----------
  #Invoca base_to_s y luego concatena el #0
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  rsbt1_to_s = Proc.new {|auto, operandos, itcond|
    base_to_s.call(auto, operandos, itcond) + ', #0'
  }

  #unpred_to_s
  #-----------
  #Indica el error
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  unpred_to_s = Proc.new {|auto, operandos, itcond|
    'ERROR: unpredictable'
  }

  #undef_to_s
  #----------
  #Indica el error
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  undef_to_s = Proc.new {|auto, operandos, itcond|
    'ERROR: undefined'
  }

  #idxbase_to_s
  #------------
  #Tres registros, el base y el índice entre paréntesis cuadrados
  #Concatena el opcode principal modificado con con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  idxbase_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = ' ' + op_s[0] + ', [' + op_s[1] + ', ' + op_s[2] + ']'
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #idx_to_s
  #--------
  #Dos valores, el segundo  entre paréntesis cuadrados
  #Concatena el opcode principal modificado con con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  idx_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = ' ' + op_s[0] + ', [' + op_s[1] + ']'
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #idxsp_to_s
  #----------
  #Dos valores, sp y el índice entre paréntesis cuadrados
  #Concatena el opcode principal modificado con con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  idxsp_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = ' ' + op_s[0] + ', [sp, ' + op_s[1] + ']'
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #opsp_to_s
  #---------
  #Dos valores, sp y el inmediato o solo un inmediato
  #Concatena el opcode principal modificado con con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  opsp_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = (op_s.length == 2) ? ' ' + op_s[0] + ', sp, ' + op_s[1] :  ' sp, sp, ' + op_s[0]
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #oppc_to_s
  #---------
  #Dos valores, pc y el inmediato
  #Concatena el opcode principal modificado con con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  oppc_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = ' ' + op_s[0] + ', pc, ' + op_s[1]
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #idxpc_to_s
  #----------
  #Dos valores, pc y el índice entre paréntesis cuadrados
  #Concatena el opcode principal modificado con con los operandos
  #separados por comas.
  #El opcode se modifica añadiendo la condición si está en
  #un bloque IT. No añade s porque siempre afecta a los flags
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  idxpc_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = ' ' + op_s[0] + ', [pc, ' + op_s[1] + ']'
    SET[auto][0] + ((itcond.nil?) ? '' : itcond) + cad
  }

  #cps_to_s
  #--------
  #Instrucción CPS. El primer operando (bit) indica
  #enable o disable. El segundo (dos bits) indica si
  #afecta a int o a fault.
  #No se permite en bloque IT
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  cps_to_s = Proc.new {|auto, operandos, itcond|
   cad = 'i' + ((operandos[0] == 0) ? 'e' : 'd') + ' '
   cad += 'i' if (operandos[1] & 2) == 2
   cad += 'f' if (operandos[1] & 1) == 1
  (itcond.nil?) ? SET[auto][0] + cad : 'ERROR: no permitida en bloque IT'
  }

  #push_to_s
  #-------------
  #Invoca basef y luego cambia x por lr
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  push_to_s = Proc.new {|auto, operandos, itcond|
    basef_to_s.call(auto, operandos, itcond).sub(/x/, 'lr')
  }

  #pop_to_s
  #--------
  #Invoca basef y luego cambia x por pc
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  pop_to_s = Proc.new {|auto, operandos, itcond|
    basef_to_s.call(auto, operandos, itcond).sub(/x/, 'pc')
  }

  #stm_to_s
  #-------------
  #Invoca basef y luego añade ! después del registro
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  stm_to_s = Proc.new {|auto, operandos, itcond|
    basef_to_s.call(auto, operandos, itcond).sub(/,/, '!,')
  }

  #ldm_to_s
  #-------------
  #Invoca basef y luego añade ! después del registro
  #si este no está en la lista
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  ldm_to_s = Proc.new {|auto, operandos, itcond|
    cad = basef_to_s.call(auto, operandos, itcond)
    (operandos[1] & (1 << operandos[0])) == 0 ? cad.sub(/,/, '!,') : cad
  }

  #bcond_to_s
  #----------
  #Función para el salto condicional b<cond>
  #Concatena el opcode principal con la condición y el operando.
  #No añade s porque siempre afecta a los flags
  #No se permite en bloque IT
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  bcond_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    cad = SET[auto][0] + op_s[0] + ' ' + op_s[1]
    (itcond.nil?) ? cad : 'ERROR: no permitida en bloque IT'
  }

  #it_to_s
  #-------
  #El tratamiento del primer operando añade t (then) o e (else) según el
  #bit coincida con el último de la condición. La primera siempre es t y
  #no modifica el nemonico, pero marca el último uno de ese operando.
  #No se permite en bloque IT
  # @param [Symbol] auto
  # @param [Array] operandos
  # @param [String] itcond
  # @return[String]
  it_to_s = Proc.new {|auto, operandos, itcond|
    op_s = ibonito(auto, operandos)
    inst = 3
    mask = 1
    $itlist = [op_s[1]] #
    cnum = operandos[1] #
    while (operandos[0] & mask) == 0 do
      inst -= 1
      mask <<= 1
    end
    cuno = 1
    mask = 8
    cad =''
    bit = operandos[1] & 1
    inst.times do
      if (operandos[0] & mask) != 0
        cuno += 1
        cad += (bit == 1) ? 't' : 'e'
        $itlist << (bit == 1) ? CONCODES[cnum] : CONCODES[cnum - 1] #
      else
        cad += (bit == 1) ? 'e' : 't'
        $itlist << (bit == 1) ? CONCODES[cnum + 1] : CONCODES[cnum] #
      end
      mask = mask / 2
    end
    p $itlist
    if (operandos[1] == 15) || ((operandos[1] == 14) && (cuno > 1))
      $itlist = nil #
      cad = 'ERROR: unpredictable'
    else
      $itlist = nil unless itcond.nil? #
      cad += ' ' + op_s[1]
      (itcond.nil?) ? SET[auto][0] + cad : 'ERROR: no permitida en bloque IT'
    end
  }

  # Lista de funciones de conversión a formato ensamblador
  FSET = { lslit1:   [lslit1_to_s],
           lsrit1:   [base_to_s],
           asrit1:   [base_to_s],
           movit1:   [base_to_s],
           cmpit1:   [basef_to_s],
           addit2:   [base_to_s],
           subit2:   [base_to_s],
           addrt1:   [base_to_s],
           subrt1:   [base_to_s],
           addit1:   [base_to_s],
           subit1:   [base_to_s],
           andrt1:   [base_to_s],
           eorrt1:   [base_to_s],
           lslrt1:   [base_to_s],
           lsrrt1:   [base_to_s],
           asrrt1:   [base_to_s],
           adcrt1:   [base_to_s],
           sbcrt1:   [base_to_s],
           rorrt1:   [base_to_s],
           tstrt1:   [basef_to_s],
           rsbrt1:   [rsbt1_to_s],
           cmprt1:   [basef_to_s],
           cmnrt1:   [basef_to_s],
           orrrt1:   [base_to_s],
           mult1:    [base_to_s],
           bicrt1:   [base_to_s],
           mvnrt1:   [base_to_s],
           addrt2:   [basef_to_s],
           unpred:   [unpred_to_s],
           cmprt2:   [basef_to_s],
           movrt1:   [basef_to_s],
           bxt1:     [basef_to_s],
           blxt1:    [basef_to_s],
           ldrlt1:   [idxpc_to_s],
           strrt1:   [idxbase_to_s],
           strhrt1:  [idxbase_to_s],
           strbrt1:  [idxbase_to_s],
           ldrsbrt1: [idxbase_to_s],
           ldrrt1:   [idxbase_to_s],
           ldrhrt1:  [idxbase_to_s],
           ldrbrt1:  [idxbase_to_s],
           ldrshrt1: [idxbase_to_s],
           strit1:   [idxbase_to_s],
           ldrit1:   [idxbase_to_s],
           strbit1:  [idxbase_to_s],
           ldrbit1:  [idxbase_to_s],
           strhit1:  [idxbase_to_s],
           ldrhit1:  [idxbase_to_s],
           strit2:   [idxsp_to_s],
           ldrit2:   [idxsp_to_s],
           adrit1:   [oppc_to_s],
           addspit1: [opsp_to_s],
           addspit2: [opsp_to_s],
           subspit1: [opsp_to_s],
           cbzt1:    [basenoit_to_s],
           sxtht1:   [basef_to_s],
           sxtbt1:   [basef_to_s],
           uxtht1:   [basef_to_s],
           uxtbt1:   [basef_to_s],
           pusht1:   [push_to_s],
           cpst1:    [cps_to_s],
           cbnzt1:   [basenoit_to_s],
           revt1:    [basef_to_s],
           rev16t1:  [basef_to_s],
           revsht1:  [basef_to_s],
           popt1:    [pop_to_s],
           bkptt1:   [nomod_to_s],
           stmt1:    [stm_to_s],
           ldmt1:    [ldm_to_s],
           udef:     [undef_to_s],
           svct1:    [basef_to_s],
           bt1:      [bcond_to_s],
           bt2:      [basenoit_to_s],
           nopt1:    [basef_to_s],
           yieldt1:  [basef_to_s],
           wfet1:    [basef_to_s],
           wfit1:    [basef_to_s],
           sevt1:    [basef_to_s],
           itt1:     [it_to_s],
           blt1:     [basenoit_to_s],
           bt4:     [basenoit_to_s]
  }

#Funciones de generacion de cadenas de instrucciones
#Llama a la función correspondiente según el tipo de
#instrucción
  def  ThumbII_Defs.to_s(tipo, operandos, dir, cond = nil)
    $address = dir
    if !$itlist.nil?
      cond = $itlist.delete_at(0)
      $itlist = nil if cond.nil?
    end
    FSET[tipo][0].call(tipo, operandos, cond)
  end

################################################
#Funciones para el funcionamiento del procesador
################################################

#reset
#-----
#Puesta a 0 del estado del procesador.
# Registros de usuario: van en un array
# Flags: en un hash indexado por nombre del flag
#Todo ello se devuelve en un Hash con símbolos
#estándar usr_regs y flags
# @return[Hash] Estado inicial del procesador
#Inicio del estado del procesador
  def ThumbII_Defs.reset
    estado = Hash.new
    usrarch = Array.new
    0.upto(15) {usrarch << 0}
    flags = {c: 0, z: 0, n: 0, v: 0}
    estado[:usr_regs] = usrarch
    estado[:flags] = flags
    return estado
  end

  #basi1r16_p
  #----------
  #Versión básica para operaciones de 16 bits con inmediato
  #El otro fuente y el destino son el mismo registro, además modifica
  #los flags -salvo que se esté en un bloque IT
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  basi1r16_p = Proc.new {|operandos, estado|
    f2 = operandos[1]
    f1 = estado[:usr_regs][operandos[0]]
    d = operandos[0]
    flags = true #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #basi2r16_p
  #----------
  #Versión básica para operaciones de 16 bits con inmediato
  #El otro fuente y el destino son dos registros, además modifica
  #los flags -salvo que se esté en un bloque IT
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  basi2r16_p = Proc.new {|operandos, estado|
    f2 = operandos[2]
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = true #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #bas3r16_p
  #---------
  #Versión básica para operaciones de 16 bits con 3 registros,
  #dos fuentes y el destino son dos registros, además modifica
  #los flags -salvo que se esté en un bloque IT
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  bas3r16_p = Proc.new {|operandos, estado|
    f2 = estado[:usr_regs][operandos[2]]
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = true #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #bas2r16_p
  #---------
  #Versión básica para operaciones de 16 bits con 2 registros,
  #uno fuente y otro fuente y destino.
  #No modifica los flags.
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  bas2r16_p = Proc.new {|operandos, estado|
    f2 = estado[:usr_regs][operandos[1]]
    f1 = estado[:usr_regs][operandos[0]]
    d = operandos[0]
    flags = false #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #bas2r16c_p
  #----------
  #Versión básica para operaciones de 16 bits con 2 registros,
  #uno fuente y otro fuente y destino.
  #Modifica los flags y añade el carry
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  bas2r16c_p = Proc.new {|operandos, estado|
    f2 = estado[:usr_regs][operandos[1]]
    f1 = estado[:usr_regs][operandos[0]]
    c = estado[:flags][:c]
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, f2: f2, c: c, d: d}
  }

  #addrsp_p
  #--------
  #Suma de un registro,
  #un inmediato y sp. El registro es destino
  #No modifica los flags.
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  addrsp_p = Proc.new {|operandos, estado|
    f2 = operandos[1] * 4
    f1 = estado[:usr_regs][SP]
    d = operandos[0]
    flags = false #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #addrpc_p
  #--------
  #Suma de un registro,
  #un inmediato y pc. El registro es destino
  #No modifica los flags.
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  addrpc_p = Proc.new {|operandos, estado|
    f2 = operandos[1] * 4
    f1 = (estado[:usr_regs][PC] & 0xFFFFFFFC) + 4
    d = operandos[0]
    flags = false #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #addisp_p
  #--------
  #Suma con el SP y un inmediato.
  #SP es fuente y destino
  #No modifica los flags.
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  addisp_p = Proc.new {|operandos, estado|
    f2 = operandos[0] * 4
    f1 = estado[:usr_regs][SP]
    d = 13
    flags = false #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 0, d: d}
  }

  #subi1r16_p
  #----------
  #Resta de 16 bits con inmediato
  #El otro fuente y el destino son el mismo registro, además modifica
  #los flags -salvo que se esté en un bloque IT
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  subi1r16_p = Proc.new {|operandos, estado|
    f2 = ~operandos[1] & 0xFFFFFFFF
    f1 = estado[:usr_regs][operandos[0]]
    d = operandos[0]
    flags = true #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 1, d: d}
  }

  #subi2r16_p
  #----------
  #Resta de 16 bits con inmediato
  #El otro fuente y el destino son dos registros, además modifica
  #los flags -salvo que se esté en un bloque IT
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  subi2r16_p = Proc.new {|operandos, estado|
    f2 = ~operandos[2] & 0XFFFFFFFF
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = true #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 1, d: d}
  }

  #sub3r16_p
  #---------
  #Resta de 16 bits con 3 registros,
  #dos fuentes y el destino son dos registros, además modifica
  #los flags -salvo que se esté en un bloque IT
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  sub3r16_p = Proc.new {|operandos, estado|
    f2 = ~estado[:usr_regs][operandos[2]] & 0xFFFFFFFF
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = true #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 1, d: d}
  }

  #subisp_p
  #--------
  #Resta con el SP y un inmediato.
  #SP es fuente y destino
  #No modifica los flags.
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  subisp_p = Proc.new {|operandos, estado|
    f2 = ~(operandos[0] * 4) & 0xFFFFFFFF
    f1 = estado[:usr_regs][SP]
    d = 13
    flags = false #revisar
    data = {fg: flags, f1: f1, f2: f2, c: 1, d: d}
  }

  #sbc2r16c_p
  #----------
  #Resta de 16 bits con 2 registros,
  #uno fuente y otro fuente y destino.
  #Modifica los flags y añade el carry
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  sbc2r16c_p = Proc.new {|operandos, estado|
    f2 = ~estado[:usr_regs][operandos[1]] & 0xFFFFFFFF
    f1 = estado[:usr_regs][operandos[0]]
    c = estado[:flags][:c]
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, f2: f2, c: c, d: d}
  }

  #rsb2r16_p
  #----------
  #Resta de 16 bits con 2 registros,
  #Resta el fuente de  0 y lo guarda en el destino.
  #Modifica los flags y añade el carry
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  rsb2r16_p = Proc.new {|operandos, estado|
    f2 = 0
    f1 = ~estado[:usr_regs][operandos[1]] & 0xFFFFFFFF
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, f2: f2, c: 1, d: d}
  }

  #cmpi1r16_p
  #----------
  #Resta de 16 bits con inmediato y descarta el resultado
  #El otro fuente es un registro
  #Modifica los flags
  #Simbolos: f1 y f2 para las fuentes, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  cmpi1r16_p = Proc.new {|operandos, estado|
    f2 = ~operandos[1] & 0xFFFFFFFF
    f1 = estado[:usr_regs][operandos[0]]
    flags = true
    data = {fg: flags, f1: f1, f2: f2, c: 1}
  }

  #cmp2r16_p
  #----------
  #Resta de 16 bits con 2 registros y descarta el resultado
  #El otro fuente es un registro
  #Modifica los flags
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  cmp2r16_p = Proc.new {|operandos, estado|
    f2 = ~estado[:usr_regs][operandos[1]] & 0xFFFFFFFF
    f1 = estado[:usr_regs][operandos[0]]
    flags = true
    data = {fg: flags, f1: f1, f2: f2, c: 1}
  }

  #cmn2r16_p
  #----------
  #Suma de 16 bits con 2 registros y descarta el resultado
  #El otro fuente es un registro
  #Modifica los flags
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  cmn2r16_p = Proc.new {|operandos, estado|
    f2 = estado[:usr_regs][operandos[1]]
    f1 = estado[:usr_regs][operandos[0]]
    flags = true
    data = {fg: flags, f1: f1, f2: f2, c: 0}
  }

  #mvn2r16_p
  #----------
  #Move negado con dos registros
  #uno fuente y otro destino.
  #Copia destino negado en fuente
  #Modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  mvn2r16_p = Proc.new {|operandos, estado|
    f1 = ~estado[:usr_regs][operandos[1]] & 0xFFFFFFFF
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, d: d}
  }

  #mov2r16_p
  #----------
  #Move con dos registros, uno fuente y otro destino.
  #Copia destino en fuente
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  mov2r16_p = Proc.new {|operandos, estado|
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = false
    data = {fg: flags, f1: f1, d: d}
  }

  #movi16_p
  #----------
  #Move con inmediato fuente y destino.
  #Copia destino en fuente
  #Modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  #c para el acarreo
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  movi16_p = Proc.new {|operandos, estado|
    f1 = operandos[1]
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, d: d}
  }

  #ldripc_p
  #--------
  #Carga desde PC + inmediato. El inmediato se multiplica
  #por 4; el pc es el actual (PC + 4) alineado en 4 por el bit
  #de modo. El otro registro es destino. Por lo demás es
  #un move.
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldripc_p = Proc.new {|operandos, estado|
    dir = operandos[1] * 4 + (estado[:usr_regs][PC] & 0xFFFFFFFC) + 4
    f1 = estado[:memory].access(:rw, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #str3rw_p
  #--------
  #Versión básica para operaciones store de un word con 3 registros.
  #El primero da el dato y los otros dos la base y el offset
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  str3rw_p = Proc.new {|operandos, estado|
    o = estado[:usr_regs][operandos[2]]
    b = estado[:usr_regs][operandos[1]]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :ww}
  }

  #str3rh_p
  #--------
  #Versión básica para operaciones store de half word con 3 registros.
  #El primero da el dato y los otros dos la base y el offset
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  str3rh_p = Proc.new {|operandos, estado|
    o = estado[:usr_regs][operandos[2]]
    b = estado[:usr_regs][operandos[1]]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :wh}
  }

  #str3rb_p
  #--------
  #Versión básica para operaciones store de un byte con 3 registros.
  #El primero da el dato y los otros dos la base y el offset
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  str3rb_p = Proc.new {|operandos, estado|
    o = estado[:usr_regs][operandos[2]]
    b = estado[:usr_regs][operandos[1]]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :wb}
  }

  #ldrsbr_p
  #--------
  #Carga de un byte con signo con modo base + offset en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrsbr_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + estado[:usr_regs][operandos[2]]
    f1 = estado[:memory].access(:rb, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      f1 = 0xffffff00 | f1 unless (f1 & 0x80) == 0
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #ldrwr_p
  #-------
  #Carga de un word con modo base + offset en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrwr_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + estado[:usr_regs][operandos[2]]
    f1 = estado[:memory].access(:rw, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #ldrhr_p
  #-------
  #Carga de un half word sin signo con modo base + offset en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrhr_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + estado[:usr_regs][operandos[2]]
    f1 = estado[:memory].access(:rh, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #ldrbr_p
  #-------
  #Carga de un byte sin signo con modo base + offset en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrbr_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + estado[:usr_regs][operandos[2]]
    f1 = estado[:memory].access(:rb, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #ldrshr_p
  #--------
  #Carga de un half word con signo con modo base + offset en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrshr_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + estado[:usr_regs][operandos[2]]
    f1 = estado[:memory].access(:rh, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      f1 = 0xffff0000 | f1 unless (f1 & 0x8000) == 0
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #str2riw_p
  #---------
  #Operaciones store de un word con 2 registros e inmediato.
  #El primero da el dato y los otros dos la base y el offset, que se multiplica por 4
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  str2riw_p = Proc.new {|operandos, estado|
    o = operandos[2] * 4
    b = estado[:usr_regs][operandos[1]]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :ww}
  }

  #str2rih_p
  #---------
  #Operaciones store de half word con 2 registros e inmediato.
  #El primero da el dato y los otros dos la base y el offset, que se multiplica por 4
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  str2rih_p = Proc.new {|operandos, estado|
    o = operandos[2] * 2
    b = estado[:usr_regs][operandos[1]]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :wh}
  }

  #str2rib_p
  #---------
  #Operaciones store de un byte con 2 registros e inmediato.
  #El primero da el dato y los otros dos la base y el offset, que se multiplica por 4
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  str2rib_p = Proc.new {|operandos, estado|
    o = operandos[2]
    b = estado[:usr_regs][operandos[1]]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :wb}
  }

  #ldrwi_p
  #-------
  #Carga de un word con modo base + offset inmediato en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrwi_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + operandos[2] * 4
    f1 = estado[:memory].access(:rw, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #ldrhi_p
  #-------
  #Carga de un half word sin signo con modo base + offset inmediato en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrhi_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + operandos[2] * 2
    f1 = estado[:memory].access(:rh, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #ldrbi_p
  #-------
  #Carga de un byte sin signo con modo base + offset inmediato en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrbi_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][operandos[1]] + operandos[2]
    f1 = estado[:memory].access(:rb, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #strisp_p
  #--------
  #Operaciones store de un word con 1 registros e inmediato.
  #El regsitro da el dato, la base es sp y el offset, que se multiplica por 4
  #No modifica los flags
  #Simbolos: f para el fuente, b para la base y o para el offset
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  strisp_p = Proc.new {|operandos, estado|
    o = operandos[1] * 4
    b = estado[:usr_regs][SP]
    f  = estado[:usr_regs][operandos[0]]
    data = {f: f, b: b, o: o, s: :ww}
  }

  #ldrisp_p
  #--------
  #Carga de un word con modo sp + offset inmediato en registro
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldrisp_p = Proc.new {|operandos, estado|
    dir = estado[:usr_regs][SP] + operandos[1] * 4
    f1 = estado[:memory].access(:rw, dir)
    if f1.is_a?(Symbol)
      data = {error: [f1, dir]}
    else
      d = operandos[0]
      flags = false
      data = {fg: flags, f1: f1, d: d}
    end
    data
  }

  #lsli_p
  #------
  #Desplazamiento lógico con dos registros -fuente y destino-
  #y un inmediato. Si el inmediato es 0, es un movs
  #Simbolos: f1 para la fuente, d para el destino, sa para el desplazamiento, fg para modificar flags.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  lsli_p = Proc.new {|operandos, estado|
    sa = operandos[2]
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, sa: sa, d: d}
  }

  #dsri_p
  #------
  #Desplazamientos a dereche con dos registros -fuente y destino-
  #y un inmediato. Si el inmediato es 0, el valor a desplazar es 32
  #Simbolos: f1 para la fuente, d para el destino, sa para el desplazamiento, fg para modificar flags.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  dsri_p = Proc.new {|operandos, estado|
    sa = operandos[2] == 0 ? 32 : operandos[2]
    f1 = estado[:usr_regs][operandos[1]]
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, sa: sa, d: d}
  }

  #shiftr_p
  #--------
  #Desplazamientos con tres registros -fuente y destino
  #en uno y desplazamiento en otro. El desplazamiento son 8 bits
  #Simbolos: f1 para la fuente, d para el destino, sa para el desplazamiento, fg para modificar flags.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  shiftr_p = Proc.new {|operandos, estado|
    sa = estado[:usr_regs][operandos[1]] & 0xFF
    f1 = estado[:usr_regs][operandos[0]]
    d = operandos[0]
    flags = true
    data = {fg: flags, f1: f1, sa: sa, d: d}
  }

  #bx_p
  #----
  #BX, copia -como move- el contenido del fuente en el pc. No modifica los flags
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  bx_p = Proc.new {|operandos, estado|
    f1 = estado[:usr_regs][operandos[0]]
    d = PC
    flags = false
    data = {fg: flags, f1: f1, d: d}
  }

  #blx_p
  #-----
  #BLX, copia -como move- el contenido del fuente en el pc y guarda retorno en LR. No modifica los flags
  #Simbolos: f1 y f2 para las fuentes, d1 y d2 para los destinos.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  blx_p = Proc.new {|operandos, estado|
    f1 = estado[:usr_regs][operandos[0]]
    f2 = (estado[:usr_regs][PC] & 0xFFFFFFFE) + 4
    d1 = PC
    d2 = LR
    data = {f1: f1, f2: f2, d1: d1, d2: d2}
  }

  #cbz_p
  #-----
  #CBZ, si el primer registro es 0 salta a PC + inmediato
  #Simbolos: f1 y f2 para la fuentes, cn para la condicion. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  cbz_p = Proc.new {|operandos, estado|
    f1 = (estado[:usr_regs][PC] & 0xFFFFFFFE) + 4
    f2 = operandos[1] * 2
    cn = estado[:usr_regs][PC] == 0
    data = {f1: f1, f2: f2, cn: cn}
  }

  #cbnz_p
  #------
  #CNBZ, si el primer registro no es 0 salta a PC + inmediato
  #Simbolos: f1 y f2 para la fuentes, cn para la condicion. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  cbnz_p = Proc.new {|operandos, estado|
    f1 = (estado[:usr_regs][PC] & 0xFFFFFFFC) + 4
    f2 = operandos[1] * 2
    cn = estado[:usr_regs][PC] != 0
    data = {f1: f1, f2: f2, cn: cn}
  }

  #ldm_p
  #-------
  #Carga de multiples words desde una dirección
  #en los registros de la lista. Si el registro de dirección no está en la lista,
  #se actualiza con el valor de la última dirección
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la lista de valores fuente, d para la lista de destinos. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  ldm_p = Proc.new {|operandos, estado|
    if(operandos.length == 2)
      base = operandos[0]
      lista = operandos[1] & 0xFF
    else
      base = SP
      lista = operandos[0] & 0x1FF
    end
    dir = estado[:usr_regs][base]
    dest = Array.new
    fnt = Array.new
    esta = false
    data = nil
    0.upto(7) do |ind|
      if lista & 1 == 1
        esta = true if base == ind
        acok = estado[:memory].access(:rw, dir)
        if acok.is_a?(Symbol)
          data = {error: [acok, dir]}
          break
        else
          fnt << acok
          dest << ind
          dir += 4
        end
      end
      lista = lista >> 1
    end
    if data.nil? && lista & 1 == 1
      acok = estado[:memory].access(:rw, dir)
      if acok.is_a?(Symbol)
        data = {error: [acok, dir]}
      else
        dest << PC
        fnt << acok
        dir += 4
      end
    end
    if esta == false
      dest << base
      fnt << dir
    end
    if data.nil?
      data = {f1: fnt, d: dest}
    else
      data[:f1] = fnt
      data[:d] = dest
    end
    data
  }

  #stm_p
  #-------
  #Almacena multiples words a partir de una dirección
  #desde los registros de la lista. El registro de dirección
  #se actualiza con el valor de la última dirección
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la lista de direcciones fuente, d1 para la lista de valores,
  # f2 para el valor del registro, d2 para el registro base. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  stm_p = Proc.new {|operandos, estado|
    base = operandos[0]
    lista = operandos[1] & 0xFF
    dir = estado[:usr_regs][base]
    dest = Array.new
    fnt = Array.new
    0.upto(7) do |ind|
      if lista & 1 == 1
        dest << estado[:usr_regs][ind]
        fnt << dir
        dir += 4
      end
      lista = lista >> 1
    end
    data = {f1: fnt, d1: dest, f2: dir, d2: base}
  }

  #push_p
  #-------
  #Almacena multiples words a partir de una dirección -4
  #desde los registros de la lista. El SP
  #se actualiza con el valor de la última dirección escrita
  #Si leemos aquí de memoria, ¿qué pasa con las excepciones?
  #No modifica los flags
  #Simbolos: f1 para la lista de direcciones fuente, d1 para la lista de valores,
  # f2 para el valor del registro, d2 para el registro base. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  push_p = Proc.new {|operandos, estado|
    base = SP
    lista = operandos[0] & 0x1FF
    dir = estado[:usr_regs][base] - 4
    dest = Array.new
    fnt = Array.new
    0.upto(7) do |ind|
      if lista & 1 == 1
        dest << estado[:usr_regs][ind]
        fnt << dir
        dir -= 4
      end
      lista = lista >> 1
    end
    if lista & 1 == 1
      dest << estado[:usr_regs][LR]
      fnt << dir
      dir -= 4
    end
    dest.reverse!
    data = {f1: fnt, d1: dest, f2: dir + 4, d2: base}
  }

  #babs_p
  #------
  #b sin condicion -salvo IT. PC + inmediato, pero este tiene signo
  #Simbolos: f1 y f2 para la fuentes, cn para la condicion. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  babs_p = Proc.new {|operandos, estado|
    f1 = (estado[:usr_regs][PC] & 0xFFFFFFFE) + 4
    f2 = operandos[0] * 2
    f2 = (f2 & 0x800 == 0) ? f2 & 0xFFF : f2 | 0xFFFFF000
    data = {f1: f1, f2: f2, cn: true}
  }

  #bcond_p
  #-------
  #b con condicion . PC + inmediato, pero este tiene signo
  #Simbolos: f1 y f2 para la fuentes, cn para la condicion. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  bcond_p = Proc.new {|operandos, estado|
    f1 = (estado[:usr_regs][PC] & 0xFFFFFFFE) + 4
    f2 = operandos[1] * 2
    f2 = (f2 & 0x100 == 0) ? f2 & 0x1FF : f2 | 0xFFFFFE00
    cn = eval_cond(operandos[0], estado[:flags])
    data = {f1: f1, f2: f2, cn: cn}
  }

  #nop_p
  #------
  #CNBZ, si el primer registro no es 0 salta a PC + inmediato
  #Simbolos: f1 y f2 para la fuentes, cn para la condicion. No modifica los flags
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  nop_p = Proc.new {|operandos, estado|
  }

  #blt1_p
  #-----
  #Específica de BL de 32 bits. Cálculo loco de la constante
  #El bit de signo S es el bit 10 del half alto, luego j1 es el bit 13
  #y j2 el 11 del half bajo. Además el half alto tiene 10 bits de inmediato con
  #con máscara 0x3FF y el bajo 11 con máscara 0x7FF.
  #Se calcula I1 = NOT(S xor J1) e igual I2 con J2, se concatena
  #S:I1:I2:Imm10:Imm11, se extiende en signo y se multiplica por 2.
  #Suma la constante con signo al pc y guarda retorno en LR. No modifica los flags
  #Simbolos: f1 y f2 para las fuentes, d1 y d2 para los destinos.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  blt1_p = Proc.new {|operandos, estado|
    numero = operandos[0]
    imm11 = numero & 0x7FF
    imm10 = (numero & 0x03FF0000) >> 5
    s = (numero & 0x04000000) == 0? 0 : 1
    j1 = (numero & 0x02000) == 0? 0 : 1
    j2 = (numero & 0x0800) == 0? 0 : 1
    i1 = (s == j1) ? 1 : 0
    i2 = (s == j2) ? 1 : 0
    imm3 = (s * 4 + i1 * 2 + i2) << 21
    imm = ((imm3 & 0x0E00000) | (imm10 & 0x1FF800) | imm11) * 2
    imm = (s == 1) ? 0xFE000000 | imm : 0x1FFFFFF & imm
    f2 = (estado[:usr_regs][PC] & 0xFFFFFFFE) + 4
    f1 = (f2 + imm)  & 0xFFFFFFFF
    d1 = PC
    d2 = LR
    data = {f1: f1, f2: f2, d1: d1, d2: d2}
  }

  #bt4_p
  #-----
  #Salto B de 32 bits. Cálculo loco de la constante
  #El bit de signo S es el bit 10 del half alto, luego j1 es el bit 13
  #y j2 el 11 del half bajo. Además el half alto tiene 10 bits de inmediato con
  #con máscara 0x3FF y el bajo 11 con máscara 0x7FF.
  #Se calcula I1 = NOT(S xor J1) e igual I2 con J2, se concatena
  #S:I1:I2:Imm10:Imm11, se extiende en signo y se multiplica por 2.
  #Suma la constante con signo al pc. No modifica los flags
  #Simbolos: f1 y f2 para la fuentes, cn, la condicion, es true.
  # @param [Array] operandos
  # @param [Hash] estado
  # @return[Hash]
  bt4_p = Proc.new {|operandos, estado|
    numero = operandos[0]
    imm11 = numero & 0x7FF
    imm10 = (numero & 0x03FF0000) >> 5
    s = (numero & 0x04000000) == 0? 0 : 1
    j1 = (numero & 0x02000) == 0? 0 : 1
    j2 = (numero & 0x0800) == 0? 0 : 1
    i1 = (s == j1) ? 1 : 0
    i2 = (s == j2) ? 1 : 0
    imm3 = (s * 4 + i1 * 2 + i2) << 21
    imm = ((imm3 & 0x0E00000) | (imm10 & 0x1FF800) | imm11) * 2
    imm = (s == 1) ? 0xFE000000 | imm : 0x1FFFFFF & imm
    f1 = (estado[:usr_regs][PC] & 0xFFFFFFFE) + 4
    f2 = imm  & 0xFFFFFFFF
    data = {f1: f1, f2: f2, cn: true}
  }
  # Lista de funciones de preparación de operandos para ejecución
  PSET = { lslit1:   [lsli_p],
           lsrit1:   [dsri_p],
           asrit1:   [dsri_p],
           movit1:   [movi16_p],
           cmpit1:   [cmpi1r16_p],
           addit2:   [basi1r16_p],
           subit2:   [subi1r16_p],
           addrt1:   [bas3r16_p],
           subrt1:   [sub3r16_p],
           addit1:   [basi2r16_p],
           subit1:   [subi2r16_p],
           andrt1:   [bas2r16c_p],
           eorrt1:   [bas2r16c_p],
           lslrt1:   [shiftr_p],
           lsrrt1:   [shiftr_p],
           asrrt1:   [shiftr_p],
           adcrt1:   [bas2r16c_p],
           sbcrt1:   [sbc2r16c_p],
           rorrt1:   [shiftr_p],
           tstrt1:   [cmn2r16_p],
           rsbrt1:   [rsb2r16_p],
           cmprt1:   [cmp2r16_p],
           cmnrt1:   [cmn2r16_p],
           orrrt1:   [bas2r16c_p],
           mult1:    [bas2r16c_p],
           bicrt1:   [sbc2r16c_p],
           mvnrt1:   [mvn2r16_p],
           addrt2:   [bas2r16_p],
           unpred:   [nop_p],        # unpred
           cmprt2:   [cmp2r16_p],
           movrt1:   [mov2r16_p],
           bxt1:     [bx_p],
           blxt1:    [blx_p],
           ldrlt1:   [ldripc_p],
           strrt1:   [str3rw_p],
           strhrt1:  [str3rh_p],
           strbrt1:  [str3rb_p],
           ldrsbrt1: [ldrsbr_p],
           ldrrt1:   [ldrwr_p],
           ldrhrt1:  [ldrhr_p],
           ldrbrt1:  [ldrbr_p],
           ldrshrt1: [ldrshr_p],
           strit1:   [str2riw_p],
           ldrit1:   [ldrwi_p],
           strbit1:  [str2rib_p],
           ldrbit1:  [ldrbi_p],
           strhit1:  [str2rih_p],
           ldrhit1:  [ldrhi_p],
           strit2:   [strisp_p],
           ldrit2:   [ldrisp_p],
           adrit1:   [addrpc_p],
           addspit1: [addrsp_p],
           addspit2: [addisp_p],
           subspit1: [subisp_p],
           cbzt1:    [cbz_p],
           sxtht1:   [mov2r16_p],
           sxtbt1:   [mov2r16_p],
           uxtht1:   [mov2r16_p],
           uxtbt1:   [mov2r16_p],
           pusht1:   [push_p],
           cpst1:    [nop_p],         #cps
           cbnzt1:   [cbnz_p],
           revt1:    [mov2r16_p],
           rev16t1:  [mov2r16_p],
           revsht1:  [mov2r16_p],
           popt1:    [ldm_p],
           bkptt1:   [nop_p],        #bkpt
           stmt1:    [stm_p],
           ldmt1:    [ldm_p],
           udef:     [nop_p],        #udef
           svct1:    [nop_p],        #svc
           bt1:      [bcond_p],
           bt2:      [babs_p],
           nopt1:    [nop_p],
           yieldt1:  [nop_p],        #yield
           wfet1:    [nop_p],        #wfe
           wfit1:    [nop_p],        #wfi
           sevt1:    [nop_p],        #sev
           itt1:     [it_to_s],
           blt1:     [blt1_p],
           bt4:      [bt4_p]
  }

  #Funciones que preparan los operandos
  #Llama a la función correspondiente según el tipo de
  #instrucción
   def ThumbII_Defs.prep_data(tipo, operandos, estado)
     PSET[tipo][0].call(operandos, estado)
   end

  #add_e
  #-----
  #Suma con acarreo. Pág. 43 del manual
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  add_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    op1 = op[:f1]
    op2 = op[:f2]
    eop1 = op1 + ((op1 & 0x80000000) << 1)
    eop2 = op2 + ((op2 & 0x80000000) << 1)
 #   sop1 = ((uop1 & 0x80000000) == 0) ? uop1 : (~uop1 + 1) & 0xFFFFFFFF
 #   sop2 = ((uop2 & 0x80000000) == 0) ? uop2 : (~uop2 + 1) & 0xFFFFFFFF
 #   ures = uop1 + uop2 + op[:c]
 #   sres = sop1 + sop2 + op[:c]
 #   res = ures & 0xFFFFFFFF
 #   ssres = ((res & 0x80000000) == 0) ? res : (~res + 1) & 0xFFFFFFFF
    #l =  [uop1, uop2, sop1, sop2, ures, sres, res, ssres]
    #p l
    #p "%X - %X - %X - %X - %X - %X - %X - %X" % l
    ures = op1 + op2 + op[:c]
    eres = eop1 + eop2 + op[:c]
    res = ures & 0xFFFFFFFF
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      c = (res == ures) ? 0 : 1
 #     v = (sres == ssres) ? 0 : 1
      dbits = (eres & 0x180000000) >> 31
      v = (dbits == 1 || dbits == 2) ? 1 : 0
      data[:flags] = {c: c, v: v, z: z, n: n}
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #and_e
  #-----
  #And bit a bit. Solo modifica N y Z
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  and_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    op1 = op[:f1]
    op2 = op[:f2]
    res = op1 & op2
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #eor_e
  #-----
  #xor bit a bit. Solo modifica N y Z
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  eor_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    op1 = op[:f1]
    op2 = op[:f2]
    res = op1 ^ op2
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #orr_e
  #-----
  #or bit a bit. Solo modifica N y Z
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  orr_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    op1 = op[:f1]
    op2 = op[:f2]
    res = op1 | op2
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #mov_e
  #-----
  #Copia fuente en destino. Solo modifica N y Z. Verifica y propaga error
  #Simbolos: f1 para la fuente, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  mov_e = Proc.new {|op|
    data = Hash.new
    if op[:error].nil?
      data[:usr_regs] = [op[:d]] unless op[:d].nil?
      res = op[:f1]
      if op[:fg]
        z = (res == 0) ? 1 : 0
        n = ((res & 0x80000000) == 0) ? 0 : 1
        data[:flags] = {z: z, n: n}
      end
      data[:usr_regs] << res unless op[:d].nil?
    else
      data[:error] = op[:error]
    end
    data
  }

  #mul_e
  #-----
  #Multiplica dos operandos y guarda los 32 bits bajos. Solo modifica N y Z
  #Simbolos: f1 y f2 para las fuentes, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  mul_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    op1 = op[:f1]
    op2 = op[:f2]
    res = (op1 * op2) & 0xFFFFFFFF
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #str_e
  #-----
  #Suma dos operandos fuente (base + offset) para formar la dirección
  #en la que guarda el tercero (fuente)
  #Revisar excepciones. Se genera un array en la entrada
  #:memory de data con los valores, por orden, del tipo de acceso,
  #y un array de pares dirección - dato (para el stm)
  #Simbolos: f para las fuente, b para la base, o para el offset, s para la operación
  # @param [Hash] op
  # @return[Hash]
  str_e = Proc.new {|op|
    mask = {ww: 0xFFFFFFFF, wh: 0xFFFF, wb: 0xFF}
    data = {memory: [op[:s], [[op[:b] + op[:o], op[:f] & mask[op[:s]]]]]}
  }

  #lsl_e
  #-----
  #Desplazamiento lógico a la izquierda. Modifica N, Z y C, excepto cuando el
  #desplazamiento es 0
  #Simbolos: f1 para la fuente, sa para el desplazamiento, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  lsl_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    if op[:sa] == 0
      res = op[:f1]
    else
      c = (op[:f1] << (op[:sa] - 1)) & 0x80000000 == 0 ? 0 : 1
      res = (op[:f1] << op[:sa]) & 0xFFFFFFFF
    end
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
      data[:flags][:c] = c unless op[:sa] == 0
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #asr_e
  #-----
  #Desplazamiento aritmético a la derecha. Modifica N, Z y C, excepto cuando el
  #desplazamiento es 0
  #Simbolos: f1 para la fuente, sa para el desplazamiento, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  asr_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    if op[:sa] == 0
      res = op[:f1]
    else
      c = (op[:f1] >> (op[:sa] - 1)) & 1 == 0 ? 0 : 1
      # msc = 0x80000000 >> (op[:sa] - 1)
      msc = (0xFFFFFFFF << (32 - op[:sa])) & 0xFFFFFFFF
      res = op[:f1] >> op[:sa]
      res = res | msc unless (op[:f1] & 0x80000000) == 0
    end
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
      data[:flags][:c] = c unless op[:sa] == 0
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #lsr_e
  #-----
  #Desplazamiento lógico a la derecha. Modifica N, Z y C, excepto cuando el
  #desplazamiento es 0
  #Simbolos: f1 para la fuente, sa para el desplazamiento, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  lsr_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    if op[:sa] == 0
      res = op[:f1]
    else
      c = (op[:f1] >> (op[:sa] - 1)) & 1 == 0 ? 0 : 1
      msc = ~(0x80000000 >> (op[:sa] - 1))
      res = (op[:f1] >> op[:sa]) & msc
    end
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
      data[:flags][:c] = c unless op[:sa] == 0
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #ror_e
  #-----
  #Rotación a la derecha, los bits que salen por la derecha entran por la izquierda.
  #Modifica N, Z y C, excepto cuando el desplazamiento es 0. C es el bit 31 del resultado
  #Simbolos: f1 para la fuente, sa para el desplazamiento, d para el destino, fg para modificar flags
  # @param [Hash] op
  # @return[Hash]
  ror_e = Proc.new {|op|
    data = Hash.new
    data[:usr_regs] = [op[:d]] unless op[:d].nil?
    if op[:sa] == 0
      res = op[:f1]
    else
      desp = op[:sa] & 0x1F
      msc = ((1 << desp) - 1) << (32 - desp)
      res = (((op[:f1] << (32 - desp)) & msc) | ((op[:f1] >> desp) & ~msc))
    end
    if op[:fg]
      z = (res == 0) ? 1 : 0
      n = ((res & 0x80000000) == 0) ? 0 : 1
      data[:flags] = {z: z, n: n}
      data[:flags][:c] = n unless op[:sa] == 0
    end
    data[:usr_regs] << res unless op[:d].nil?
    data
  }

  #blx_e
  #-----
  #Copia fuente 1 en destino 1 y f2 en d2. No modifica flags
  #Simbolos: f1 y f2 para las fuentes, d1 y d2 para los destinos
  # @param [Hash] op
  # @return[Hash]
  blx_e = Proc.new {|op|
    data = {usr_regs: [op[:d1], op[:f1], op[:d2], op[:f2]]}
  }

  #cbxz_e
  #------
  #Suma las dos fuentes y las escribe en pc si la condición es cierta. No modifica flags
  #Simbolos: f1 y f2 para las fuentes, cn para la condición
  # @param [Hash] op
  # @return[Hash]
  cbxz_e = Proc.new {|op|
    data = op[:cn] ? {usr_regs: [PC, op[:f1] + op[:f2]]} : Hash.new
  }

  #sxth_e
  #------
  #Extiende en signo el half de fuente y lo pone en destino. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  sxth_e = Proc.new {|op|
    valor = op[:f1] & 0x8000 == 0 ? op[:f1] & 0xFFFF : op[:f1] | 0xFFFF0000
    data = {usr_regs: [op[:d], valor]}
  }

  #sxtb_e
  #------
  #Extiende en signo el byte de fuente y lo pone en destino. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  sxtb_e = Proc.new {|op|
    valor = op[:f1] & 0x80 == 0 ? op[:f1] & 0xFF : op[:f1] | 0xFFFFFF00
    data = {usr_regs: [op[:d], valor]}
  }

  #uxth_e
  #------
  #Extiende con ceros el half de fuente y lo pone en destino. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  uxth_e = Proc.new {|op|
    data = {usr_regs: [op[:d], op[:f1] & 0xFFFF]}
  }

  #uxtb_e
  #------
  #Extiende con ceros el byte de fuente y lo pone en destino. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  uxtb_e = Proc.new {|op|
    data = {usr_regs: [op[:d], op[:f1] & 0xFF]}
  }

  #rev_e
  #------
  #Invierte el orden de los bytes de fuente lo pone en destino. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  rev_e = Proc.new {|op|
    val = ((op[:f1] << 24) & 0xFF000000) | ((op[:f1] << 8) & 0xFF0000) | ((op[:f1] >> 8) & 0xFF00) | ((op[:f1] >> 24) & 0xFF)
    data = {usr_regs: [op[:d], val]}
  }


  #rev16_e
  #-------
  #Invierte el orden de los bytes de cada half lo pone en destino. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  rev16_e = Proc.new {|op|
    val = ((op[:f1] << 8) & 0xFF00FF00) | ((op[:f1] >> 8) & 0xFF00FF)
    data = {usr_regs: [op[:d], val]}
  }

  #revsh_e
  #-------
  #Invierte el orden de los bytes del half inferior y lo pone en destino extendido en signo. No modifica flags
  #Simbolos: f1 para la fuente y d para el destino
  # @param [Hash] op
  # @return[Hash]
  revsh_e = Proc.new {|op|
    val = ((op[:f1] << 8) & 0xFF00) | ((op[:f1] >> 8) & 0xFF)
    val = val & 0x8000 == 0 ? val & 0xFFFF : val | 0xFFFF0000
    data = {usr_regs: [op[:d], val]}
  }

  #ldm_e
  #-----
  #Guarda registros múltiples, propaga el error
  #Simbolos: f1 para la lista de fuente y d para la lista de destinos
  # @param [Hash] op
  # @return[Hash]
  ldm_e = Proc.new {|op|
    res = Array.new
    data = Hash.new
    if !op[:d].nil?
      op[:d].each.with_index do |item, ind|
        res << item
        res << op[:f1][ind]
      end
    data[:usr_regs] = res
    end
    data[:error] = op[:error] unless op[:error].nil?
    data
  }

  #stm_e
  #-----
  #Suma dos operandos fuente (base + offset) para formar la dirección
  #en la que guarda el tercero (fuente)
  #Revisar excepciones. Se genera un array en la entrada
  #:memory de data con los valores, por orden, del tipo de acceso,
  #y un array de pares dirección - dato (para el stm)
  #Simbolos: f1 para la lista de direcciones, d1 para la lista de valores
  # f2 para el valor del registro y d2 para el registro
  # @param [Hash] op
  # @return[Hash]
  stm_e = Proc.new {|op|
    res = Array.new
    op[:d1].each.with_index do |item, ind|
      res << [op[:f1][ind], item]
    end
    data = {usr_regs: [op[:d2], op[:f2]], memory: [:ww, res]}
  }

  #nop_e
  #------
  #No hace nada
  # @param [Hash] op
  # @return[Hash]
  nop_e = Proc.new {|op|
    data = Hash.new
  }

   # Lista de funciones para ejecución de instrucciones
   ESET = { add:   [add_e],
            and:   [and_e],
            eor:   [eor_e],
            orr:   [orr_e],
            mov:   [mov_e],
            mul:   [mul_e],
            ldr:   [mov_e],      #por si acaso
            str:   [str_e],
            strh:  [str_e],
            strb:  [str_e],
            adr:   [add_e],
            lsl:   [lsl_e],
            lsr:   [lsr_e],
            asr:   [asr_e],
            ror:   [ror_e],
            bx:    [mov_e],
            blx:   [blx_e],
            cbz:   [cbxz_e],
            cbnz:  [cbxz_e],
            sxth:  [sxth_e],
            sxtb:  [sxtb_e],
            uxth:  [uxth_e],
            uxtb:  [uxtb_e],
            rev:   [rev_e],
            rev16: [rev16_e],
            revsh: [revsh_e],
            ldm:   [ldm_e],
            pop:   [ldm_e],
            stm:   [stm_e],
            push:  [stm_e],
            unp:   [nop_e],
            cps:   [nop_e],
            bkpt:  [nop_e],
            und:   [nop_e],
            svc:   [nop_e],
            yield: [nop_e],
            wfe:   [nop_e],
            wfi:   [nop_e],
            sev:   [nop_e],
            b:     [cbxz_e],
            nop:   [nop_e]
   }

   #Funciones de ejecución
  #Llama a la función correspondiente según el tipo de
  #instrucción
  def ThumbII_Defs.execute(tipo, datos)
    ESET[SET[tipo][1]][0].call(datos)
  end
end