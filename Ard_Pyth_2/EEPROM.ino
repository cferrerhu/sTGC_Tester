
 void EEPROM_write(uint8_t uiAddress, unsigned char ucData)
{
 /* Wait for completion of previous write */
 while(EECR & (1<<EEPE));
 /* Set up address and Data Registers */
 EEARH &= ~0b00000011;
 EEARL = uiAddress;
 EEDR = ucData;
 /* Write logical one to EEMPE */
 EECR |= (1<<EEMPE);
 /* Start eeprom write by setting EEPE */
 EECR |= (1<<EEPE);
}

uint8_t EEPROM_read(uint8_t uiAddress)
{
 /* Wait for completion of previous write */
 while(EECR & (1<<EEPE));
 /* Set up address register */
 EEARH &= ~0b00000011;
 EEARL = uiAddress;
 /* Start eeprom read by writing EERE */
 EECR |= (1<<EERE);
 /* Return data from Data Register */
 return EEDR;
}

//void guardarEEPROM(uint8_t dir, uint8_t val){
//  if(EEPROM_read(dir)!=val)EEPROM_write(dir,val);
//}
//
//
//void EEPROM_init(){
//  cuenta_max=EEPROM_read(dir_refresco);
//  //cuenta_max=EEPROM_read(dir_refresco)*60;
//  cuenta=cuenta_max+1;
//}
