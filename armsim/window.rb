require 'wx'
require_relative 'instruction'
require_relative 'coder'
require_relative 'core'
include Wx

class MyFrame < Frame
  def initialize()
    @proc = Core.new
    @c = Coder.new
    custom_size = Size.new(250, 300)
    super(nil, -1, 'SimCortex M3 V -1.0', DEFAULT_POSITION, custom_size)
    @my_panel = Panel.new(self)
    @my_label = StaticText.new(@my_panel, -1, 'Instrucciones Thumb de 16 bits',
                               DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @my_label2 = StaticText.new(@my_panel, -1, 'Introduce un opcode: ',
                                 DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @my_textbox = TextCtrl.new(@my_panel, -1, '0x0000')
    #@my_combo = ComboBox.new(@my_panel, -1, 'Default Combo Text', DEFAULT_POSITION, DEFAULT_SIZE, ['Item 1', 'Item 2', 'Item 3'])
    @my_button_d = Button.new(@my_panel, -1, 'Decodificar')
    @my_answer = StaticText.new(@my_panel, -1, '-----',
                               DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)
    @my_button_e = Button.new(@my_panel, -1, 'Ejecutar')
    @my_state = StaticText.new(@my_panel, -1, '',
                                DEFAULT_POSITION, DEFAULT_SIZE, ALIGN_CENTER)

    evt_button(@my_button_d.get_id()) { |event| my_button_d_click(event)}
    evt_button(@my_button_e.get_id()) { |event| my_button_e_click(event)}
    update_state

    @my_panel_row = BoxSizer.new(HORIZONTAL)        #
    @my_panel_row.add(@my_label2, 0, GROW|ALL, 2)   #
    @my_panel_row.add(@my_textbox, 0, GROW|ALL, 2)  #
    @my_panel_sizer = BoxSizer.new(VERTICAL)
    @my_panel.set_sizer(@my_panel_sizer)

    @my_panel_sizer.add(@my_label, 0, GROW|ALL, 2)
    @my_panel_sizer.add(@my_panel_row, 0, GROW|ALL, 2) #
    #@my_panel_sizer.add(@my_textbox, 0, GROW|ALL, 2)
    #@my_panel_sizer.add(@my_combo, 0, GROW|ALL, 2)
    @my_panel_sizer.add(@my_button_d, 0, GROW|ALL, 2)
    @my_panel_sizer.add(@my_answer, 0, GROW|ALL, 2)
    @my_panel_sizer.add(@my_button_e, 0, GROW|ALL, 2)
    @my_panel_sizer.add(@my_state, 0, GROW|ALL, 2)

    show()
  end

  def my_button_d_click(event)
    opc = (@my_textbox.get_line_text 0).hex
    @i = @c.decode([opc])
    @my_answer.set_label(@i.to_s)
    @my_answer.center_on_parent(HORIZONTAL)
  end

  def update_state
    tring = ''
    0.upto(4) do |ind|
      tring += "R%d:  %08X              " % [2 * ind, @proc.reg(2 * ind)]
      tring += "R%d:  %08X\n" % [2 * ind + 1, @proc.reg(2 * ind + 1)]
    end
    tring += "R10: %08X              " % @proc.reg(10)
    tring += "R11: %08X\n" % @proc.reg(11)
    tring += "R12: %08X              " % @proc.reg(12)
    tring += "SP:  %08X\n" % @proc.reg(13)
    tring += "LR:  %08X              " % @proc.reg(14)
    tring += "PC:  %08X\n" % @proc.reg(15)
    tring += "\nC: %d - Z: %d - N: %d - V: %d" % [@proc.flag(:c), @proc.flag(:z), @proc.flag(:n), @proc.flag(:v)]
    @my_state.set_label(tring)
    @my_state.center_on_parent(HORIZONTAL)
  end

  def my_button_e_click(event)
    @proc.execute(@i) unless @i.nil?
    update_state
  end
end

class MyApp < App
  def on_init
    MyFrame.new
  end
end

MyApp.new.main_loop()