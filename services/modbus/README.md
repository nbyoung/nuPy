## Demo using [Modpoll](https://www.modbusdriver.com/modpoll.html) as the Modbus master

* In the demo code
  * Define a Modbus data model comprising five _Holding_ registers
  * Assign initial values of `1`, `2`, `3`, `4`, `5`

**`demo_modbus_slave_tcp.py`**
```
modbusDataModel = data.Model((1, 2, 3, 4, 5))
```

* Use _modpoll_ to read five registers from the slave
  * `-a 255` Modbus slave address 255
  * `-c 5` Count five registers
  * `-r 1` Starting with register 1
  * `-1` Reading once (i.e., no repeat polling)
  * `192.168.1.11` TCP slave address

**`$ modpoll -a 255 -c 5 -r 1 -1 192.168.1.11`**
```
modpoll 3.9 - FieldTalk(tm) Modbus(R) Master Simulator
Copyright (c) 2002-2020 proconX Pty Ltd
Visit https://www.modbusdriver.com for Modbus libraries and tools.

Protocol configuration: MODBUS/TCP, FC3
Slave configuration...: address = 255, start reference = 1, count = 5
Communication.........: 192.168.1.11, port 502, t/o 1.00 s, poll rate 1000 ms
Data type.............: 16-bit register, output (holding) register table

-- Polling slave...
[1]: 1
[2]: 2
[3]: 3
[4]: 4
[5]: 5
```

* Write the values `10`, `20`, `30`, `40`, `50`
  
**`$ modpoll -a 255 -c 5 -r 1 192.168.1.11 10 20 30 40 50`**
```
...
Written 5 references.
```

* Read back the written values

**`$modpoll -a 255 -c 5 -r 1 -1 192.168.1.11`**
```
...
-- Polling slave...
[1]: 10
[2]: 20
[3]: 30
[4]: 40
[5]: 50
```

