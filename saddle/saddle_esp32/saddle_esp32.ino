/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updates by chegewara
*/
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"

// need to add more of these for other values!
#define CHARACTERISTIC_UUID_ONE "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHARACTERISTIC_UUID_TWO "478a3421-a04c-4978-8e4d-00cb8eea9af6"


BLECharacteristic *pCharacteristic[2]; // change size as needed

class PressureCallbacks : public BLECharacteristicCallbacks {
  void onRead(BLECharacteristic *pChar) {
    // replace this with something that loads new values from whatever sensor you use
    pChar->setValue(String(pChar->getValue().toInt() + 1));
  }
};

void setup() {

  Serial.begin(115200);
  Serial.println("Starting BLE work!");

  BLEDevice::init("BEATS Device");
  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  pCharacteristic[0] =
    pService->createCharacteristic(CHARACTERISTIC_UUID_ONE, BLECharacteristic::PROPERTY_READ);

  pCharacteristic[0]->setCallbacks(new PressureCallbacks());

  pCharacteristic[0]->setValue(String(101325)); // adjust this to a visibly reset value

  pCharacteristic[1] =
    pService->createCharacteristic(CHARACTERISTIC_UUID_TWO, BLECharacteristic::PROPERTY_READ);

  pCharacteristic[1]->setCallbacks(new PressureCallbacks());

  pCharacteristic[1]->setValue(String(0)); // adjust this to a visibly reset value

  pService->start();

  // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("Setup complete!");
}

void loop() {
  // callbacks mean that technically nothing needs to happen here for BLE alone.
}