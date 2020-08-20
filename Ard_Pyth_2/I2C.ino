
uint8_t leerI2C(uint8_t dir, uint8_t reg){
  uint8_t puerto=0xFF;
  
  Wire.beginTransmission(dir); // Dirección I2C
  Wire.write(reg); 
  Wire.endTransmission();

  Wire.requestFrom(dir, 1);
  while(Wire.available() == 0);
  puerto = Wire.read();   
  return puerto; 
}


void escribirI2C(uint8_t dir, uint8_t reg, uint8_t valor){
   Wire.beginTransmission(dir);
   Wire.write(reg); 
   Wire.write(valor);
   Wire.endTransmission();
}





void scan(){

 
   byte error, add;
  int nDevices;
  for(add = 0; add < 7; add++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address[add]);
    error = Wire.endTransmission();
 
    if (error == 0)
    {
      Serial.print("Mult "); 
      Serial.print(nom[add]);
      Serial.println(" OK"); 
 
      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Mult "); 
      Serial.print(nom[add]);
      Serial.println(" ERROR"); 
    }    
  }
  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
}
