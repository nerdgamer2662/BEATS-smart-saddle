// Copyright 2017-2023, Charles Weinberger & Paul DeMarco.
// All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

import 'screens/bluetooth_off_screen.dart';
import 'screens/scan_screen.dart';

void main() {
  FlutterBluePlus.setLogLevel(LogLevel.info, color: true);
  runApp(const FlutterBlueApp());
}

//
// This widget shows BluetoothOffScreen or
// ScanScreen depending on the adapter state
//
class FlutterBlueApp extends StatefulWidget {
  const FlutterBlueApp({super.key});

  @override
  State<FlutterBlueApp> createState() => _FlutterBlueAppState();
}

class _FlutterBlueAppState extends State<FlutterBlueApp> {

  int pVal = 0;

  void setNewP(int newP) {
    setState(() {
      pVal = newP;
    });
  }

  @override
  void initState() {
    super.initState();
    checkSupport();

    late StreamSubscription<BluetoothAdapterState> subscription;
    subscription = FlutterBluePlus.adapterState.listen((BluetoothAdapterState state) {
      print(state);
      if (state == BluetoothAdapterState.on) {
        subscription.cancel();
      } else {
          if (Platform.isAndroid) {
            FlutterBluePlus.turnOn(); // Request the user to turn on Bluetooth
            subscription.cancel();
          }
      }
    });

    bleScan();
  }

  Future<void> checkSupport() async {
    if (!await FlutterBluePlus.isSupported) { print("Bluetooth not supported by this device"); }
    else { print("Yay! Bluetooth support!"); }
  }

  Future<void> bleScan() async {

    var scanSubscription = FlutterBluePlus.onScanResults.listen((results) async {
      if (results.isNotEmpty) {
        ScanResult r = results.last;
        print('${r.device.remoteId}: "${r.advertisementData.advName}" found!');

        if (r.advertisementData.advName == "BEATS Device") {
          FlutterBluePlus.stopScan();
          r.device.connectionState.listen((BluetoothConnectionState state) async {
            if (state == BluetoothConnectionState.connected) {
              print("Connection established!");

              List<BluetoothService> services = await r.device.discoverServices();
              for (var service in services) {
                print(service.uuid);
                
              }
            } else if (state == BluetoothConnectionState.disconnected) {
              print("Disconnected");
            }
          });
          await r.device.connect(autoConnect: true, mtu: null);
        }
      }
    }, onError: (e) => print(e));

    FlutterBluePlus.cancelWhenScanComplete(scanSubscription);

    await FlutterBluePlus.startScan(
      timeout: Duration(seconds: 10),
    );


  }

  @override
  void dispose() {
    super.dispose();

  }

  @override
  Widget build(BuildContext context) {

    return MaterialApp(
      color: Colors.lightBlue,
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        body: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text("Pressure: "),
            Text(pVal.toString()),
          ],
        ),
      ),
    );
  }
}