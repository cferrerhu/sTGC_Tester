




void USART_Init(uint16_t vel){

  uint16_t ubrr = (F_CPU/16/vel)-1; // velocidad baud rat
  //UBRR0H = (ubrr>>8);
  UBRR0L = 103;

  UCSR0B |= (1<<RXEN0)|(1<<TXEN0);// |(1<<RXCIE0);

  UCSR0C &= ~_BV(UPM00);
  UCSR0C &= ~_BV(UPM01);
  
  UCSR0C |=  _BV(UCSZ00);
  UCSR0C |=  _BV(UCSZ01);
  
  UCSR0C &= ~_BV(USBS0);  

  _delay_ms(100);
}

void USART_Transmit_String(char* string)
{
  while(*string != 0){
    while ( !( UCSR0A & (1<<UDRE0)) );
    UDR0 =*string;
    string++;
  }
}

void USART_Transmit_Stringln(char* string)
{
  while(*string != 0){
    while ( !( UCSR0A & (1<<UDRE0)) );
    UDR0 =*string;
    string++;
  }
  //while ( !( UCSR0A & (1<<UDRE0)) );
  //  UDR0 =13;
   while ( !( UCSR0A & (1<<UDRE0)) );
   UDR0 =10;
}

void USART_Transmit_char(uint8_t data)
{
  while ( !( UCSR0A & (1<<UDRE0)) ); //espera la ultima transmision
   UDR0 =data;
}
