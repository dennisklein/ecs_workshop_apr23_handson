## Support Files for Hands-on Session Fri 9am

[Experiment Control System Workshop April 23, GSI Darmstadt](https://indico.gsi.de/event/17490)

### Preparation

```console
> git clone https://github.com/dennisklein/ecs_workshop_apr23_handson
> cd ecs_workshop_apr23_handson
> python -m venv env
> . env/bin/activate
> pip install caproto
> pip install git+https://github.com/Yakifo/amqtt.git#egg=amqtt
```

Repeat this in every new shell:
```console
> cd ecs_workshop_apr23_handson
> . env/bin/activate
```

### Run the demo

Run the EPICS IOC:
```console
python -m caproto.ioc_examples.random_walk --list-pvs --interface 127.0.0.1
```

Run the MQTT broker:
```console
amqtt
```

Run the demo script:
```console
export EPICS_CA_AUTO_ADDR_LIST=NO
export EPICS_CA_ADDR_LIST=127.0.0.1
python -m demo
```

Stop any of the programs via Ctrl+C.
