#include <Wire.h>
#define F_CPU  16000000UL
#include <avr/io.h>
#include <string.h>
#include <util/delay.h>

uint8_t OE = 6;

uint8_t RST = 3;
uint8_t INT = 2;

bool led = 0;

uint8_t dev = 7;

char nom [7]= {'A','B','C','D','E','F','G'};
uint8_t address[7]= {0x20,0x21,0x22,0x23,0x24,0x25,0x26};

uint8_t Inputs_reg[5] = {0x00,0x01,0x02,0x03,0x04}; // Input Port registers (solo leer)
uint8_t Outputs_reg[5] = {0x08,0x09,0x0A,0x0B,0x0C}; // Output Port registers ()
uint8_t Polarity_reg[5] = {0x10,0x11,0x12,0x13,0x14}; // Polarity Inversion registers input (0-> normal, 1->invertida)
uint8_t Config_reg[5] = {0x18,0x19,0x1A,0x1B,0x1C}; // I/O Configuration registers (0-> output, 1->input)
uint8_t Interrupt_reg[5] = {0x20,0x21,0x22,0x23,0x24}; // Mask Interrupt registers (0-> genera interrupción, 1->no genera interrupción)


uint8_t OUTCONF_reg = 0x28; //output structure configuration register (0-> open-drain, 1->totem-pole)
uint8_t MODE_reg = 0x2A; // MODE - mode selection register (address 2Ah) description

int tiempo_set = 50;
int corriente = 0;

uint8_t ADC_sel = 0;

int cuenta=1;
uint8_t actual[3] = {0,0,0};

uint8_t incoming[10] = {1,2,3,4,5,6,7,8,9,10};

bool debug = false; //Mostrar menos

void setup() {
  
  Wire.begin();
  Serial.begin(57600);
  pinSetup();
  InitADC();
  //IntSetup();

 // ## [#,E,0,0,0,$] Read errors and send them back
 // [#,I,0,0,0,
while (read_serial() != 35);
scan();
Serial.println("#,I,$,");


  
}

void loop() {
  // put your main code here, to run repeatedly:
  read_comand();
}



void read_comand(){
  while (read_serial() != 35);
 
  uint8_t i = 0;
  bool cond = true;
  
  while (cond){
    uint8_t info = read_serial();
    if(info>33 && info<250){
      if(debug)Serial.print(info);
      if (info == 36) cond = false;
      else{
        incoming[i] = info;
        i++;
      }
      }
   } 
   cases();
}


void cases(){
  uint8_t letter = incoming[0];
  if(debug)Serial.print(letter);
  
  switch(letter){
    
    case 83://S
    
    break;
        
    case 87://W

    if(ADC_sel){
      digitalWrite(OE,1);
      pinHigh(incoming[1]-48, incoming[2]-48, 1<<(incoming[3]-48));
      delay(tiempo_set);
      digitalWrite(OE,0);
      corriente = ReadADC(ADC_sel);
      digitalWrite(OE,1);
    }

    else{
      pinHigh(incoming[1]-48, incoming[2]-48, 1<<(incoming[3]-48));
      delay(tiempo_set);
      corriente = ReadADC(ADC_sel);  
    }

    pinLow(incoming[1]-48, incoming[2]-48, 1<<(incoming[3]-48));

    Serial.print(incoming[0]-48);
    Serial.print(",");
    Serial.print(incoming[1]-48);
    Serial.print(",");
    Serial.print(incoming[2]-48);
    Serial.print(",");
    Serial.print(incoming[3]-48);
    Serial.print(",");
    Serial.println(corriente);

    break;
        
    case 69://E
    pinHigh(incoming[1]-48, incoming[2]-48, 1<<(incoming[3]-48));
    delay(tiempo_set);
    buscarCC();
    Serial.print("R");
    Serial.print(",");
    Serial.print(incoming[1]-48);
    Serial.print(",");
    Serial.print(incoming[2]-48);
    Serial.print(",");
    Serial.print(incoming[3]);
    Serial.print(",");
    Serial.println("$");
    break;
        
    case 80://P
    if(incoming[1]==73){ //73=I
      //InitTimer1(true);
      ADC_sel = 1;
      for(uint8_t i=0;i<10;i++)ReadADC(ADC_sel);
      delay(tiempo_set);
      Serial.println("Timer on");
    }
    else{
      digitalWrite(OE,0);
      //InitTimer1(false);
      ADC_sel = 0;
      delay(tiempo_set);
      Serial.println("Timer off");
    }
    break;

    default:
    Serial.println("Error");
    break;
  }
}





char read_serial(){
  if(Serial.available() > 0); uint8_t data=Serial.read();
  return data;
}

void pinSetup(){
  pinMode(RST,OUTPUT);
  digitalWrite(RST,LOW);
  delay(tiempo_set);
  digitalWrite(RST,HIGH);

  //pinMode(INT,INPUT_PULLUP);
  DDRD &= ~(1 << DDD2); //pines de interrupción
  PORTD |= (1 << PORTD2);
  
  pinMode(A7,INPUT); //ADC pin 7
  pinMode(A6,INPUT); //ADC pin 7
  pinMode(13,OUTPUT); //Led
  
  

    pinMode(OE,OUTPUT);
    digitalWrite(OE,1);
  
  

 for(uint8_t a=0;a<dev;a++){
   // Output como totem pole
   escribirI2C(address[a],OUTCONF_reg,0xFF);
   escribirI2C(address[a],MODE_reg,0b00000000);

  //Configurar todos como inputs
   for(uint8_t i=0;i<5;i++){
    escribirI2C(address[a],Config_reg[i],0xFF);
    escribirI2C(address[a],Interrupt_reg[i],0x00);
   }
 }
  
}


//
//void SMBALERT(){
// Wire.requestFrom(0b00011001, 1);
// while(Wire.available() == 0);
// uint8_t valor = Wire.read();
// Serial.println(valor,HEX);
//}



void InitTimer1(bool estado)
{
  if (estado){
    pinMode(OE, OUTPUT); // output pin for OCR0B  
    // Set up the 8MHz output
    TCCR0A = _BV(COM0A1) | _BV(COM0B1) | _BV(WGM01) | _BV(WGM00);
    TCCR0B = _BV(WGM02) | _BV(CS00);
    OCR0A = 100;
    OCR0B = 50;
    if(debug){
      Serial.println("Timern encendido");
    }
    ADC_sel = 1;
  }
  else{
    TCCR0A = ~(_BV(COM0A1) | _BV(COM0B1));
    if(debug){
      Serial.println("Timern apagado");
    }
    ADC_sel = 0;
  }
}


void IntSetup(){
  EICRA |= (1 << ISC00); //set INT0 to trigger on ANY logic change
  EIMSK |= (1 << INT0); // External Interrupt Request 0 Enable
  sei();
}

ISR (INT0_vect)
{
  digitalWrite(13,~(PORTD & (1 << PORTD2)));
}
