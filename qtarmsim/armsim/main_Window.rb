require 'wx'
require_relative 'thumbII_Defs'
require_relative 'instruction'
require_relative 'coder'
require_relative 'core'
require_relative 'memory'
require_relative 'memory_block'
require_relative 'read_ELF'
include Wx

GCC = 'C:\Users\German\Documents\GitHub\Arduino\build\windows\work\hardware\tools\g++_arm_none_eabi\bin\arm-none-eabi-gcc.exe'
CL1 = '-mcpu=cortex-m1 -mthumb -c'
CL3 = '-mcpu=cortex-m1 -mthumb -c'

class MainWindow < Frame

  #initialize
  #----------
  # Creamos la ventana y el motor de funcionamiento.
  # Recibimos el procesador como parámentro, con la memoria ya configurada
  def initialize(procesador)
    @proc = procesador
    #El decodificador es cosa de la interfaz. Así podemos cambiar desde ella distintas características
    @coder = Coder.new
    #Creamos la ventana con un tamaño adecuado y las características que tocan
    custom_size = Size.new(700, 550)
    super(nil, -1, 'SimCortex M3 V -1.0', DEFAULT_POSITION, custom_size)
    #Creamos dos paneles, uno para registros e instrucciones y otro para memoria
    #Los añadimos a través de un sizer ocupando cada uno su fracción de la ventana
    @reg_panel = Panel.new(self)
    @mem_panel = Panel.new(self)
    main_sizer = BoxSizer.new(HORIZONTAL)
    set_sizer(main_sizer)
    main_sizer.add(@reg_panel,13, ALIGN_CENTER | GROW | ALL, 0)
    main_sizer.add(@mem_panel,15, ALIGN_CENTER | GROW | ALL, 0)
    @color = @reg_panel.get_background_colour
    @mem_panel.set_background_colour(WHITE)

    #Establecemos los objetos del panel de registros.
    #Título del panel, cuadro de entrada de inst. y texto asociado,
    #botón de decodificar, inst. decodificada, botón de ejecutar decodificada
    #y de ejecutar paso a paso.
    @titulo = StaticText.new(@reg_panel, -1, @proc.arch,
                               DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @titulo.set_foreground_colour(BLUE)
    @my_label2 = StaticText.new(@reg_panel, -1, 'Introduce un opcode: ',
                                DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @my_textbox = TextCtrl.new(@reg_panel, -1, '0x0000')
    @button_decode = Button.new(@reg_panel, -1, 'Decodificar')
    @my_answer = StaticText.new(@reg_panel, -1, '-----',
                                DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER | ST_NO_AUTORESIZE)
    @button_exedec = Button.new(@reg_panel, -1, 'Ejecutar decodificada')
    @button_exepc = Button.new(@reg_panel, -1, 'Paso a paso')
    #Organizamos en una fila el texto y caja de decodificación
    @decode = BoxSizer.new(HORIZONTAL)
    @decode.add(@my_label2, 0, GROW|ALL, 2)
    @decode.add(@my_textbox, 0, GROW|ALL, 2)
    #Organizamos en una fila los botones de ejecución
    @exe = BoxSizer.new(HORIZONTAL)
    @exe.add(@button_exedec, 1, ALIGN_CENTER|ALL, 2)
    @exe.add(@button_exepc, 1, ALIGN_CENTER|ALL, 2)

    #Objetos para el estado
    #Array de nombres y valores de registros. Se organizan en dos columnas mediante
    #un array de 8 sizers horizontales
    @nreg = %w(R0: R1: R2: R3: R4: R5: R6: R7: R8: R9: R10: R11: R12: SP: LR: PC:)
    @vreg = Array.new
    @estado = Array.new
    0.upto(15) do |ind|
      @nreg[ind] = StaticText.new(@reg_panel, -1, @nreg[ind],
                                 DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT)
      @vreg[ind] = StaticText.new(@reg_panel, -1, '0x00000000',
                                 DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_RIGHT | ST_NO_AUTORESIZE)
    end
    0.upto(7) do |ind|
      box = BoxSizer.new(HORIZONTAL)
      box.add(@nreg[ind], 3, ALIGN_LEFT|ALL, 2)
      box.add(@vreg[ind], 9, ALIGN_RIGHT|ALL, 2)
      box.add_stretch_spacer(3)
      box.add(@nreg[8 + ind], 3, ALIGN_LEFT|ALL, 2)
      box.add(@vreg[8 + ind], 9, ALIGN_RIGHT|ALL, 2)
      @estado[ind] = box
    end
    #Los flags son un simple texto en una línea
    @flags = StaticText.new(@reg_panel, -1, 'C: 0 - Z: 0 - N: 0 - V: 0',
                                DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER | ST_NO_AUTORESIZE)
    #Y creamos el título de la zona de estado
    @title_estado = StaticText.new(@reg_panel, -1, 'Estado del procesador',
                                   DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER | ST_NO_AUTORESIZE)
    @title_estado.set_foreground_colour(BLUE)

    #Objetos para la memoria de instrucciones
    #Tiene tres componentes (dirección, word e instrucción)
    #luego tanto el título como los datos son filas de tres objtos
    #Así creamos el título en azul y con borde 2
    @title_mem = BoxSizer.new(HORIZONTAL)
    st = StaticText.new(@reg_panel, -1, 'Direccion',
                        DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
    st.set_foreground_colour(BLUE)
    @title_mem.add(st, 3, ALIGN_LEFT|ALL, 2)
    st = StaticText.new(@reg_panel, -1, 'Codigo w1',
                        DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
    st.set_foreground_colour(BLUE)
    @title_mem.add(st, 2, ALIGN_LEFT|ALL, 2)
    st = StaticText.new(@reg_panel, -1, 'w2',
                        DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
    st.set_foreground_colour(BLUE)
    @title_mem.add(st, 2, ALIGN_LEFT|ALL, 2)
    st = StaticText.new(@reg_panel, -1, 'Instruccion',
                        DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
    st.set_foreground_colour(BLUE)
    @title_mem.add(st, 5, ALIGN_LEFT|ALL, 2)
    #Para los datos, hemos de relacionar lo mostrado con el PC, por eso guardamos
    #un array con las direcciones mostradas y el número de entradas, y el array con las filas de tres objetos
    #Los datos de las filas los leemos de la memoria a que apunta el PC tras el reset
    #El del PC lo resaltamos con fondo CYAN
    @imem = Array.new
    @listpc = Array.new
    @sizimem = 9
    pc = @proc.reg(15)
    0.upto(9) do |ind|
      @listpc << 2 * ind + pc
      box = BoxSizer.new(HORIZONTAL)
      word = @proc.memory_half(2 * ind + pc)
      word2 = @proc.memory_half(2 * ind + pc + 2)
      label = $symbol_table.key(2 * ind + pc)
      label = label.nil? ? "0x%08X" % (2 * ind + pc) : label
      st = StaticText.new(@reg_panel, -1, label,
                     DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
      st.set_background_colour(CYAN) if ind == 0
      box.add(st, 3, ALIGN_LEFT|ALL, 2)
      st = StaticText.new(@reg_panel, -1, "0x%04X" % word,
                    DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
      st.set_background_colour(CYAN) if ind == 0
      box.add(st, 2, ALIGN_LEFT|ALL, 2)
      inst = @coder.decode([word, word2], 2 * ind + pc)
      pc = pc + 2 if inst.size == 2
      lbl = (inst.size == 2) ? "0x%04X" % word2 : ''
      st = StaticText.new(@reg_panel, -1, lbl,
                          DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
      st.set_background_colour(CYAN) if ind == 0
      box.add(st, 2, ALIGN_LEFT|ALL, 2)
      st = StaticText.new(@reg_panel, -1, inst.to_s,
                          DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_LEFT | ST_NO_AUTORESIZE)
      st.set_background_colour(CYAN) if ind == 0
      box.add(st, 5, ALIGN_LEFT|ALL, 2)
      @imem[ind] = box
    end

    #Asignamos los callbacks de los botones
    evt_button(@button_decode.get_id()) { |event| button_decode_click(event)}
    evt_button(@button_exedec.get_id()) { |event| button_exedec_click(event)}
    evt_button(@button_exepc.get_id()) { |event| button_exepc_click(event)}

    #Ahora asignamos el sizer vertical al panel de registros y lo llenamos
    @reg_panel_sizer = BoxSizer.new(VERTICAL)
    @reg_panel.set_sizer(@reg_panel_sizer)

    @reg_panel_sizer.add(@titulo, 0, GROW|ALL, 2)
    @reg_panel_sizer.add(@decode, 0, GROW|ALL, 2)
    @reg_panel_sizer.add(@button_decode, 0, GROW|ALL, 2)
    @reg_panel_sizer.add(@my_answer, 0, GROW|ALL, 2)
    @reg_panel_sizer.add(@exe, 0, GROW|ALL, 2)
    @reg_panel_sizer.add(@title_estado, 0, GROW|ALL, 2)
    0.upto(7) do |ind|
      @reg_panel_sizer.add(@estado[ind], 0, GROW|ALL, 2)
    end
    @reg_panel_sizer.add(@flags, 0, GROW|ALL, 2)
    @reg_panel_sizer.add(@title_mem, 0, GROW|ALL, 2)
    0.upto(9) do |ind|
      @reg_panel_sizer.add(@imem[ind], 0, GROW|ALL, 0)
    end

    #Establecemos los objetos del panel de memoria.
    @titulo_mem = StaticText.new(@mem_panel, -1, 'Memoria de datos',
                             DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @titulo_mem.set_foreground_colour(BLUE)
    @titulo_stack = StaticText.new(@mem_panel, -1, 'PILA',
                                 DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @titulo_stack.set_foreground_colour(BLUE)
    @data_mem = gen_mem_w(ORIG_DATA, 16)
    #La direccion de pila tiene el SP a la mitad, así que es SP - 8 * 4 *4
    @stack_mem = gen_mem_w(@proc.reg(ThumbII_Defs::SP) - 128, 12)
    #Ahora asignamos el sizer vertical al panel de memoria y lo llenamos
    @mem_panel_sizer = BoxSizer.new(VERTICAL)
    @mem_panel.set_sizer(@mem_panel_sizer)
    @mem_panel_sizer.add(@titulo_mem, 0, GROW|ALL, 2)
    0.upto(15) do |ind|
      @mem_panel_sizer.add(@data_mem[ind], 0, GROW|ALL, 0)
    end
    @mem_panel_sizer.add(@titulo_stack, 0, GROW|ALL, 2)
    0.upto(15) do |ind|
      @mem_panel_sizer.add(@stack_mem[ind], 0, GROW|ALL, 0)
    end

    #Actualizamos los valores de reset de registros por si acaso
    #y mostramos la ventana
    update_state
    show()
  end

  #update_imem
  #-----------
  #Actualiza la memoria de instrucciones en función del PC
  #Si la instrucción del PC está en pantalla, simplemente
  #la resalta con fondo CYAN. Para no tener que guardar el
  #PC anterior, incialmente se borran todos los fondos.
  #Si el PC no está en pantalla, construya toda la lista
  #desde el PC y resalta la posición 0
  def update_imem
    pc = @proc.reg(15)
    idx = @listpc.find_index(pc)
    if idx == nil
      @imem.each do |sizer|
        word = @proc.memory_half(pc)
        word2 = @proc.memory_half(pc + 2)
        w = sizer.get_children[0].get_window
        label = $symbol_table.key(pc)
        label = label.nil? ? "0x%08X" % (pc) : label
        w.set_label(label)
        w.set_background_colour(@color)
        w = sizer.get_children[1].get_window
        w.set_label("0x%04X" % word)
        w.set_background_colour(@color)
        w = sizer.get_children[2].get_window
        inst = @coder.decode([word, word2], pc)
        pc = pc + 2 if inst.size == 2
        lbl = (inst.size == 2) ? "0x%04X" % word2 : ''
        w.set_label(lbl)
        w.set_background_colour(@color)
        w = sizer.get_children[3].get_window
        w.set_label(inst.to_s)
        w.set_background_colour(@color)
        pc += 2
      end
      0.upto(3) do |ind|
        @imem[0].get_children[ind].get_window.set_background_colour(CYAN)
      end
    else
      @imem.each do |sizer|
        0.upto(3) do |ind|
          sizer.get_children[ind].get_window.set_background_colour(@color)
        end
      end
      0.upto(3) do |ind|
        @imem[idx].get_children[ind].get_window.set_background_colour(CYAN)
      end
    end
  end

  def gen_mem_w(dir, rows)
    mem = Array.new
    c = Colour.new(0, 0, 100)
    1.upto(rows) do
      box = BoxSizer.new(HORIZONTAL)
      w = StaticText.new(@mem_panel, -1, "0x%08X:" % dir,
                         DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_RIGHT | ST_NO_AUTORESIZE)
      w.set_foreground_colour(c)
      box.add_stretch_spacer(1)
      box.add(w, 9, ALIGN_RIGHT|ALL, 2)
      box.add_stretch_spacer(1)
      1.upto(4) do
        w = StaticText.new(@mem_panel, -1, "0x%08X" % @proc.memory_word(dir),
                           DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_RIGHT | ST_NO_AUTORESIZE)
        box.add(w, 9, ALIGN_RIGHT|ALL, 2)
        dir += 4
      end
      mem << box
    end
    return mem
  end

  def update_mem_w(set, dir)
    set.each do |sizer|
      w = sizer.get_children[1].get_window
      w.set_label("0x%08X:" % dir)
      3.upto(6) do |lind|
        w = sizer.get_children[lind].get_window
        w.set_label("0x%08X" % @proc.memory_word(dir))
        dir += 4
      end
    end
  end

  #update_state
  #------------
  #Actualiza el valor de todos los registros y los flags escribiendo en los objetos correspondientes
  def update_state
    0.upto(15) do |ind|
      @vreg[ind].set_label("0x%08X" % @proc.reg(ind))
    end
    tring = "C: %d - Z: %d - N: %d - V: %d" % [@proc.flag(:c), @proc.flag(:z), @proc.flag(:n), @proc.flag(:v)]
    @flags.set_label(tring)
  end

  #Callback del botón de decodificación
  #Lee el valor de la caja como una cifra hexadecimal, la decodifica
  #a una instrucción y la muestra.
  #La instrucción es global porque podremos ejectuarla
  def button_decode_click(event)
    opc = (@my_textbox.get_line_text 0).hex
    if (opc & 0xFFFF0000) == 0
      opc2 = 0
    else
      opc2 = opc & 0xFFFF
      opc = (opc >> 16) & 0xFFFF
    end
    @i = @coder.decode([opc, opc2])
    @my_answer.set_label(@i.to_s)
  end

  #Callback del botón de ejecución de inst. decodificada
  #Ejecuta la instrucción decodificada, si existe,
  #y actualiza el estado
  def button_exedec_click(event)
    @proc.execute(@i) unless @i.nil?
    update_state
  end

  #Callback del botón de ejecución paso a paso
  #Ejecuta la instrucción del pc si existe -debería existir
  #y actualiza el estado y la memoria de instrucciones
  def button_exepc_click(event)
    word = @proc.memory_half(@proc.reg(15))
    word2 = @proc.memory_half(@proc.reg(15) + 2)
    inst = @coder.decode([word, word2])
    @proc.execute(inst) unless inst.nil?
    update_state
    update_imem
    update_mem_w(@data_mem, ORIG_DATA)
    update_mem_w(@stack_mem, @proc.reg(ThumbII_Defs::SP) - 128)
    refresh
  end
end

def read_ELF
    ELF_File.open('c:\add.o', 'rb') do |file|
    e_ident = file.get_array(16)
    magic = e_ident[1].chr + e_ident[2].chr + e_ident[3].chr
    puts("MAGIC: 0x%02X %s" % [e_ident[0], magic])
    puts("CLASS: %s" % ELFCLASS[e_ident[4]])
    puts("DATA:  %s" % ELFCLASS[e_ident[5]])
    puts(ELFVERSION[e_ident[6]])
    e_type = file.get_half
    puts(ELFTYPE[e_type])
    e_machine = file.get_half
    puts("MACHINE:%d (ARM)" % e_machine)
    e_version = file.get_word
    puts(ELFVERSION[e_version])
    e_entry = file.get_word
    puts("Entry point address: %d" % e_entry)
    e_phoff = file.get_word
    puts("Program header table offset: %d" % e_phoff)
    e_shoff = file.get_word
    puts("Section header table offset: %d" % e_shoff)
    e_flags = file.get_word
    p e_flags
    e_ehsize = file.get_half
    puts("ELF header size: %d" % e_ehsize)
    e_phentsize = file.get_half
    puts("Program header table entry size: %d" % e_phentsize)
    e_phnum = file.get_half
    puts("Program header table entries: %d" % e_phnum)
    e_shentsize = file.get_half
    puts("Section header table entry size: %d" % e_shentsize)
    e_shnum = file.get_half
    puts("Section header table entries: %d" % e_shnum)
    e_shstrndx = file.get_half
    puts("Section name string table index: %d" % e_shstrndx)

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
      puts cursec
    end
    file.wks_orig['.rodata'] = file.wks_orig['.text'] + file.sections[file.wks['.text']].header[:size]
    file.wks_orig['.rodata'] += 4 - (file.wks_orig['.rodata'] % 4) unless (file.wks_orig['.rodata'] % 4) == 0
    file.wks_orig['.bss'] = file.wks_orig['.data'] + file.sections[file.wks['.data']].header[:size]
    p file.wks
    p file.wks_orig
    file.seek(file.sections[stable].header[:offset], IO::SEEK_SET)
    num = file.sections[stable].header[:size] / file.sections[stable].header[:entsize]
    puts "Symbol table idx: %d, entries: %d, at file offset: %d" % [stable, num, file.sections[stable].header[:offset]]
    puts "File size: %d, section end: %d\n" % [file.size, file.sections[stable].header[:offset] + file.sections[stable].header[:size] - 1 ]
    file.symbols = Array.new
    0.upto(num - 1) do |idx|
      cursym = SymbolTableEntry.new
      cursym.idx = idx
      cursym.data = file.get_symbol_entry
      cursym.name = file.get_string_table_string(cursym.data[:name])
      file.symbols << cursym
    end
    file.symbols.each do |cursec|
      puts cursec
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
      end
      file.relocations << relocations
    end
    file.relocations.each do |cursec|
      puts "Tabla"
      cursec.each do |entry|
        puts entry
      end
    end
    # Nos preparamos. Lo primero es leer las secciones con datos
    file.fill_section(file.wks['.text']) unless file.sections[file.wks['.text']].header[:size] == 0;
    p file.sections[file.wks['.text']].data
    file.fill_section(file.wks['.data']) unless file.sections[file.wks['.data']].header[:size] == 0;
    p file.sections[file.wks['.data']].data
    file.fill_section(file.wks['.rodata']) unless file.sections[file.wks['.rodata']].header[:size] == 0;
    p file.sections[file.wks['.rodata']].data

    return file.relocate

  end
end

class MainApp < App

  #A través del Core procesador podemos acceder a todo
  attr_reader :procesador

  #on_init
  #-------
  #Aquí pondremos toda la inicialización y esas cosas
  #de momento una ROM random, la RAM de datos y la pila
  def on_init
    blocks = read_ELF
    @procesador = Core.new(ThumbII_Defs::ARCH, blocks[0])
    @procesador.memory.add_block(blocks[1])
    @procesador.memory.symbolTable = blocks[2]
    $symbol_table = blocks[2]
    @procesador.update({usr_regs: [ThumbII_Defs::PC, ORIG_CODE, ThumbII_Defs::SP, END_DATA - 128]})
    MainWindow.new(@procesador)
  end
end

MainApp.new.main_loop()