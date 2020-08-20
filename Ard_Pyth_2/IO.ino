

void pinHigh(uint8_t dir, uint8_t reg, uint8_t palabra){
    escribirI2C(address[dir],Config_reg[reg],~palabra);
    escribirI2C(address[dir],Outputs_reg[reg],palabra);

}

void pinLow(uint8_t dir, uint8_t reg, uint8_t palabra){
    escribirI2C(address[dir],Outputs_reg[reg],0x00);
    escribirI2C(address[dir],Config_reg[reg],0xFF);
}

uint8_t leerPuerto(uint8_t dir, uint8_t reg){
  uint8_t puerto=0xFF;
  puerto = leerI2C(address[dir], Inputs_reg[reg]);

  return puerto; 
}

void buscarCC(){
  uint8_t val=0xFF;
  
  for(uint8_t a=0;a<dev;a++){  
    for(uint8_t i=0;i<5;i++){
    val=leerPuerto(a,i);
    if(val>0){
      for(uint8_t pos=0;pos<8;pos++){
        if((val>>pos)&1){
            Serial.print("C");
            Serial.print(",");
            Serial.print(nom[a]);
            Serial.print(",");
            Serial.print(i);
            Serial.print(",");
            Serial.print(pos);
            Serial.print(",");
            Serial.print(val);
            Serial.println("$");
         }
        }
    }
   }
 }

}



void leer_puertos(){
    for(uint8_t a=0;a<dev;a++){
  //Leer puertos
   for(uint8_t i=0;i<5;i++){
    Serial.print("Mult: ");
    Serial.print(a);
    Serial.print(", Puerto: ");
    Serial.print(i);
    Serial.print(", Val:  ");
    Serial.print(leerPuerto(a, i));
    Serial.print(", INT:  ");
    Serial.println(leerI2C(address[a],Interrupt_reg[i]));
   }
 }
}
