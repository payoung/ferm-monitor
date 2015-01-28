#include <OneWire.h>

int pin = 2;
OneWire ds(pin);

void setup(void) {
  Serial.begin(9600);
}

void loop() {
	
  byte present = 0;
  byte data[12];
  byte addr[8];
  float temp;
  byte i;
  
  if (!ds.search(addr)) {
    ds.reset_search();
  }

  if ( OneWire::crc8( addr, 7) != addr[7]) {
      Serial.print("CRC is not valid!\n");
      return;
  }
  
  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);
  delay(1000);
  present = ds.reset();
  ds.select(addr);
  ds.write(0xBE);
  for (int i = 0; i < 9; i++) {
    data[i] = ds.read();
  }
  temp = ((data[1] << 8) + data[0])*0.0625;
  for( i = 0; i < 8; i++) {
    Serial.print(addr[i], HEX);
  }
  Serial.print(" ");
  Serial.print(temp);
  Serial.print("\n");

}
