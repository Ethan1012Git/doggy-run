from machine import Pin, PWM, ADC, I2C
import ssd1306
import random as rand
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

vert = ADC(Pin(32))
horz = ADC(Pin(35))
 
vert.atten(ADC.ATTN_11DB)
horz.atten(ADC.ATTN_11DB)

button = Pin(17, Pin.IN, Pin.PULL_UP)
button1 = Pin(5, Pin.IN, Pin.PULL_UP)
button2 = Pin(36, Pin.IN, Pin.PULL_UP)


speaker_pin = Pin(14)
speaker_pwm = PWM(speaker_pin)
speaker_pwm.duty(0)

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0) 
oled.show()

level_up = [392,494,587,784,415,523,622,831,466,587,698,932]
    
p = [
0x30, 0x30, 0x48, 0x48, 0x48, 0x48, 0x4f, 0x84, 0x80, 0x04, 0x80, 0x04, 0x82, 0x12, 0x82, 0x12, 0x80, 0x02, 0x81, 0x52, 0x81, 0x51, 0x81, 0xf1, 0x80, 0x01, 0x80, 0x01, 0x40, 0x01, 0x3f, 0xfe
]
t =[
0x00, 0x00, 0x01, 0x00, 0x09, 0x20, 0x09, 0x20, 0x09, 0x20, 0x0f, 0xe0, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00
]

highest_score = 0

def draw_character(data, x, y):
    for row in range(16):  # 遍歷每一行，因為我們的字型是16x16的點陣圖
        for byte_index in range(2):  # 因為我們是以8位的byte來存儲，一行需要2個byte（16位元）
            # 根據行數和位元組索引來計算我們在資料中的位置
            byte_val = data[row * 2 + byte_index]  
            # 計算X軸的起始位置。我們知道每個位元組有8個點，所以乘以8
            x_0 = x + byte_index * 8
            # 計算Y軸的位置，因為我們在遍歷每一行時，y座標會增加
            y_0 = y + row
            for bit in range(8):  # 遍歷位元組中的每一位
                # 這裡我們使用一個遮罩來檢查byte_val中的特定位元是否為1。
                # 1 << (7 - bit) 會產生如下的遮罩: 10000000, 01000000, ... , 00000001
                # 然後我們用位元與運算(&)來檢查byte_val的這一位是否被設為1。
                if byte_val & (1 << (7 - bit)): 
                    oled.pixel(x_0 + bit, y_0, 1)  # 如果是1，則在OLED上繪製一個點
class game():
    
    def start(highest_score): 
        oled.text("Highest:"+str(highest_score),28,14)
        oled.text("Press Joystick",8,28)
        oled.text("To Start!",32,44)
        oled.show()
    
    def get_height(v,h,top,speed):
        if v < 1500:
            if not top:
                speed -= 1
                if speed == 0:
                    top = True
                else:
                    h -= speed    
        else:
            top = True
        if top:
            speed+=1
            h+=speed
        if h>=39:
            first = True
            h = 39
            top = False
            speed = 10
        
        return h,top,speed

    def update(h,score,summon,t_x,d):
        oled.fill(0)
        if summon:
            t_x -= d
            if t_x < -10:
                summon = False
            else:
                draw_character(t,t_x,39)
        oled.hline(0, 56, 128, 1)
        oled.text("score:"+str(score),0,0)
        draw_character(p,2,h)
        oled.show()
        return summon,t_x
        
    def summon_t(summon):
        r = rand.randrange(10)
        if r < 1:
            summon = True
        return summon
    
    def is_alive(h,x,summon):
        if x <= 14 and h >=24 and x >= -8 and summon:
            return False
        return True
    
    def diff_add():
        for i in level_up:
            speaker_pwm.freq(i)
            speaker_pwm.duty(512)
            time.sleep(0.03)
            speaker_pwm.duty(0) 
            time.sleep(0.03)
            
                
def play():
    alive = True
    top = False
    h = 39
    score = 0
    summon = False
    d = 3
    speed = 10
    while alive:
        v = vert.read()
        if not summon:
            t_x = 128
            summon = game.summon_t(summon)
        score +=1
        if score % 1000 == 0 and d < 10:
            d+=1
            game.diff_add()
            
        h, top,speed = game.get_height(v,h,top,speed)
        summon,t_x = game.update(h,score,summon,t_x,d)
        alive = game.is_alive(h,t_x,summon)
    return score
    

while True:
    game.start(highest_score)
    b = not button.value()
    if b:
        score = play()
        if score > highest_score:
            highest_score = score
        
        
        
    
        
    
        
        
        

    
        
        
    

