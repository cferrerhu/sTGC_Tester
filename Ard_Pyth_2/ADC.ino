
uint16_t ReadADC(uint8_t num) //0 main ADC, 1 peak detector
{
 //select ADC channel with safety mask
 if (num)
 { ADMUX = 0b11000110;
 }
 else{
  ADMUX = 0b11000111; 
 }
 //single conversion mode
 ADCSRA |= (1<<ADSC);
 // wait until ADC conversion is complete
 while( ADCSRA & (1<<ADSC) );
 return ADC; 
}


void InitADC() 
{
 //ADMUX |= (1<<REFS0); //  Vref=AVcc
 ADMUX |= (1<<REFS0)|(1<<REFS1); // Vref=1.1V interno

 //set prescaller to 128 and enable ADC 
 ADCSRA |= (1<<ADEN);    
}
