# GINTRONIC V2
import time
from time import sleep
import machine
from machine import I2C, Pin, UART
from i2c_lcd import I2cLcd
from rotary_irq_rp2 import RotaryIRQ

# DEF GLOBAL VARIABLES
lcd = I2cLcd(I2C(1, sda=machine.Pin(14), scl=machine.Pin(15), freq=400000), 0x27, 4, 20)
uart = UART(0, 9600)
led = Pin(5, Pin.OUT)
index = -1
cocktails = []
pumps = []
button_pin = Pin(12, Pin.IN, Pin.PULL_UP)
r = RotaryIRQ(
    pin_num_clk=11,
    pin_num_dt=10,
    reverse=False,
    incr=1,
    range_mode=RotaryIRQ.RANGE_UNBOUNDED,
    pull_up=True,
    half_step=False,
)


# rotary = Rotary(10, 11, 12)


# DEF CLASS
class cocktail:
    def __init__(self, name, listPumps):
        self.name = name
        self.listPumps = listPumps
        # self.numPumps = len(self.listPumps)

    def execute_cocktail(self):  # DEF EXECUTE
        lcd.clear()
        lcd.putstr("Wait for            " + self.name + " ")
        pump_list = self.listPumps.copy()
        sec = 0
        max_sec = 0
        for npump in pump_list:
            npump.on()
            print()
            sleep(0.2)
            print("Accendo ", npump.number)
            sleep(0.2)
            # if npump.sec >=max_sec:
            #    max_sec = npump.sec
        while pump_list:
            sleep(1)
            sec = sec + 1
            for npump in pump_list:
                if npump.sec <= sec:
                    print("tolgo " + npump.number)
                    pump_list.remove(npump)
                    npump.off()
                sleep(0.2)
                # lcd.move_to(12,2)
                # lcd.putstr(str(int(sec*100/max_sec))+ "%" )
                lcd.move_to(12, 1)
                lcd.putstr(str(int(sec)) + "s")
        blink_twice()
        reset_lcd()

    def set_name(self, name):
        self.name = name

    def str(self):
        string_complete = self.name
        for pompa in self.listPumps:
            string_complete = string_complete + ", P:" + pompa.number + ", " + str(pompa.sec) + " s."
        return string_complete


class pump:
    def __init__(self, number, pin, sec):
        self.number = number
        self.pinn = pin
        self.pin = Pin(pin, Pin.OUT)
        self.pin.value(1)
        self.sec = sec

    def set_sec(self, sec):
        self.sec = int(sec)

    def on(self):
        self.pin.value(0)

    def off(self):
        self.pin.value(1)


# DEF FUNCTION
''' CHANGE THE SELECTED DRINK'''


def blink_twice():
    led.value(1)
    sleep(0.5)
    led.value(0)
    sleep(0.5)
    led.value(1)
    sleep(0.5)
    led.value(0)


'''
def update_index(val_max): 
    global index, selected
    xValue = xAxis.read_u16()
    selected = button.value()
    if xValue <= 600:
        index = (index-1)%val_max
        lcd.clear()
        lcd.putstr(cocktails[index].name)
    if xValue >= 60000:
        index = (index+1)%val_max
        insert_lcd(cocktails[index].name)
    sleep(0.2)


def is_selected(): 
    if button.value() == 1:
        return True
    return False
'''


def rotary_changed():
    global index, val_max
    val_new = r.value()
    if index != val_new% len(cocktails):
        index = val_new % len(cocktails)
        print(cocktails[index].name)
        lcd.clear()
        lcd.putstr(cocktails[index].name)
    elif not button_pin.value():
        print('RELEASE')
        cocktails[index].execute_cocktail()
    time.sleep_ms(50)


''' RESET THE LCD '''


def reset_lcd():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("COCKTAIL MACHINE")
    lcd.move_to(0, 1)
    lcd.putstr("Move and choose cocktail!")


def insert_lcd(testo):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("COCKTAIL MACHINE")
    lcd.move_to(0, 1)
    lcd.putstr(testo)


''' MODIFY COCKTAIL VALUE '''
comandi = "modsecpump-1-10 : setto a 10 i secondi della pompa 1  \n\r " \
          " moddrinkname-gintonic-gintonics : cambio il nome di gintonic " \
          "in gintonics \n\r  removepump-americano-3  tolgo al cocktail americano " \
          "la pompa 3\n\r  addpump-americano-5 aggioungo al cocktail americano la " \
          "pompa 5 \n\r  "
comandi = comandi + "adddrink-cosmopolitano-5-6-7 creo cosmopolitan con pompe 5-6-7  \n\r  "
comandi = comandi + "deldrink-americano : elimino il cocktail di nome americano  \n\r "
''' '''


def update_cocktail(data):
    msg = data.decode('utf-8')
    print("Leggo : " + msg)
    lcd.clear()
    lcd.putstr(msg)
    sleep(2)
    reset_lcd()
    msg_part = msg.split("-")

    if msg_part[0] == 'ciao':
        print_cocktails()

    elif msg_part[0] == 'modsecpump':  # MOD PUMP SEC (pump_number, sec)
        print("Cambio secondi pompa")
        print(msg.split("-")[1:])
        find_and_set_sec(msg_part[1], msg_part[2])
        sleep(1)
        reset_lcd()
        save_pumps()

    elif msg_part[0] == 'moddrinkname':  # MOD DRINK NAME(old_name, new_name)
        print("Cambio nome drink")
        print(msg.split("-")[1:])
        find_and_set_name(msg_part[1], msg_part[2])
        sleep(1)
        reset_lcd()
        save_cocktails()

    elif msg_part[0] == 'removepump':  # DEL A PUMP TO A DRINK (cocktail_name, pump_number)
        print("Rimuovo pompa")
        lcd.clear()
        lcd.putstr("Rimuovo pompa")
        print(msg.split("-")[1:])
        mod_pump(msg_part[1], msg_part[2], 0)
        sleep(1)
        reset_lcd()
        save_cocktails()

    elif msg_part[0] == 'addpump':  # ADD A PUMP TO A DRINK (cocktail_name, pump_number)
        print("Aggiungo pompa")
        lcd.clear()
        lcd.putstr("Aggiungo pompa")
        print(msg_part[2])
        mod_pump(msg_part[1], msg_part[2], 1)
        sleep(1)
        reset_lcd()
        save_cocktails()

    elif msg_part[0] == 'adddrink':  # ADD A DRINK (name, pump_number)
        print("Aggiungo drink")
        lcd.clear()
        lcd.putstr("Aggiungo drink")
        print(msg.split("-")[1:])
        cocktails.append((msg_part[1], return_pumps(msg_part[2:])))
        sleep(1)
        reset_lcd()
        save_cocktails()

    elif msg_part[0] == 'deldrink':  # REMOVE DRINK (name)
        print("Rimuovo drink")
        lcd.clear()
        lcd.putstr("Rimuovo drink")
        print(msg.split("-")[1:])
        find_and_del_cocktails(msg_part[1])
        sleep(1)
        reset_lcd()
        save_cocktails()

    elif msg_part[0] == 'save':
        save()
    elif msg_part[0] == 'read':
        read()
    elif msg_part[0] == 'help':
        print_bt(comandi)
    else:
        lcd.clear()
        lcd.putstr("Comando non riconosciuto")
        sleep(1)
        reset_lcd()


''' BLUETOOTH FUNCTION '''


def find_and_set_sec(num, sec):
    for pompa in pumps:
        if pompa.number == num:
            pompa.set_sec(sec)
            print("setto " + num + " a " + str(sec))
            lcd.putstr("Pompa n:" + num + " sec: " + str(sec))
            sleep(1)
            reset_lcd()
    print_cocktails()


def find_and_set_name(old_name, new_name):
    for drink in cocktails:
        if drink.name == old_name:
            drink.set_name(new_name)
            lcd.clear()
            lcd.putstr("Nome cambiato in " + new_name)
            sleep(1)
            reset_lcd()
    print_cocktails()
    save_cocktails()


def mod_pump(cocktail_name, pump_name, val):
    for drink in cocktails:
        if drink.name == cocktail_name:
            for pin in pumps:
                if pump_name == pin.number:
                    if not val:
                        if pin in drink.listPumps:
                            drink.listPumps.remove(pin)
                    elif val:
                        if pin not in drink.listPumps:
                            drink.listPumps.append(pin)


def find_and_del_cocktails(name):
    for drink in cocktails:
        if drink.name == name:
            cocktails.remove(drink)


def print_bt(testo):
    uart.write(testo + "\n\r")


def print_all(testo):
    print(testo)
    print_bt(testo)


def print_cocktails():
    for drink in cocktails:
        print_all(drink.str() + "\n\r")


# LOAD AND SAVE

def save():
    save_pumps()
    save_cocktails()


def read():
    read_pumps()
    read_cocktails()


''' FOR DRINKS '''


# READ COCKTAILS
def read_cocktails():
    lcd.clear()
    lcd.putstr("Loading cocktails")
    with open('cocktails.json', 'r') as fr:
        test = fr.readlines()
        for el in test:
            el = el.replace("\n", "").replace("\r", "").split(",")
            print(el)
            drink = build_cocktail(el[0], el[1:])
            cocktails.append(drink)
    fr.close()
    sleep(1)
    reset_lcd()


def build_cocktail(name, list_numbers):
    list_pumps = return_pumps(list_numbers)
    return cocktail(name, list_pumps)


def return_pumps(list_number):
    lista = []
    for number in list_number:
        for pompa in pumps:
            if number == pompa.number:
                lista.append(pompa)
    return lista


# SAVE COCKTAILS
def save_cocktails():
    lcd.clear()
    lcd.putstr("Saving cocktials")
    with open('cocktails.json', 'w') as f:
        for drink in cocktails:
            line = drink.name
            for pompa in drink.listPumps:
                line += "," + pompa.number
            f.write(line + "\n")
    f.close()
    sleep(1)
    reset_lcd()


''' FOR PUMPS '''


# SAVE PUMPS
def save_pumps():
    lcd.clear()
    lcd.putstr("Saving pumps")
    with open('pumps.json', 'w') as f:
        for pompa in pumps:
            f.write(pompa.number + "," + str(pompa.pinn) + "," + str(pompa.sec) + "\n")
    f.close()
    sleep(1)
    reset_lcd()


# READ PUMPS
def read_pumps():
    lcd.clear()
    lcd.putstr("Loading pumps")
    with open('pumps.json', 'r') as fr:
        file_lines = fr.readlines()
        for line in file_lines:
            line = line.replace("\n", "").replace("\r", "").split(",")
            print(line)
            pumps.append(pump(line[0], int(line[1]), int(line[2])))
    fr.close()
    sleep(1)
    reset_lcd()


################ INIT ################

pumps = [pump("1",16,2),
         pump("2",17,2),
         pump("3",18,2),
         pump("4",19,2),
         pump("5",20,2),
         pump("6",21,2),
         pump("7",22,2),
         pump("8",28,10)
        ]


cocktails =[cocktail("Americano",pumps[0:2]),
            cocktail("GinTonic",pumps[2:4]),
            cocktail("Spritz",pumps[4:6]),
            cocktail("Vino",pumps[6:7])
            ]





# START
def init():
    lcd.putstr("Set up")
    read_pumps()
    sleep(1)
    read_cocktails()
    sleep(1)
    reset_lcd()
    while True:
        if uart.any() > 0:
            update_cocktail(uart.readline())
        rotary_changed()


if __name__ == "__main__":
    init()
