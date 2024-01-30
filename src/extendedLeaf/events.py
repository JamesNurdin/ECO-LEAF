from src.extendedLeaf.power import PowerDomain, validate_str_time


class PowerDomainEvent:
    def __init__(self, event, args, time_str, repeat=False, repeat_counter=30):
        self.event = event
        self.args = args
        self.time = time_str
        self.time_int = PowerDomain.get_current_time(self.time)
        self.repeat = repeat
        if repeat is True:
            if isinstance(repeat_counter, str):
                if validate_str_time(repeat_counter):
                    self.repeat_counter = PowerDomain.get_current_time(repeat_counter)
            elif isinstance(repeat_counter, int):
                if repeat_counter > 0:
                    self.repeat_counter = repeat_counter
            else:
                raise ValueError(f"Error: invalid time increment provided")

            self.current_counter = 0

    def __call__(self, *args, **kwargs):
        self.event(*args)


class EventDomain:
    def __init__(self, env, update_interval=1, start_time_str="00:00:00"):
        self.env = env
        self.update_interval = update_interval
        self.events = []
        self.event_history = []
        self.start_time_index = PowerDomain.get_current_time(start_time_str)

    def add_event(self, power_domain_event):
        self.events.append(power_domain_event)

    def run(self):
        while True:
            yield self.env.timeout(self.update_interval)
            self.run_events()

    def run_events(self):
        current_time = self.env.now + self.start_time_index
        events_to_remove = []
        for event in self.events:
            if current_time >= event.time_int:
                event(*event.args)
                self.event_history.append(event)
                events_to_remove.append(event)
                if event.repeat:
                    new_event_time_str = PowerDomain.convert_to_time_string(event.time_int + event.repeat_counter)
                    new_event = PowerDomainEvent(event=event.event, args=event.args, time_str=new_event_time_str,
                                                        repeat=True, repeat_counter=event.repeat_counter)
                    new_event.time_int = event.time_int + event.repeat_counter
                    self.events.append(new_event)

        for event in events_to_remove:
            self.events.remove(event)
