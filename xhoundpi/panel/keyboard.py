''' Human input controller based on PC keyboard '''

from pynput.keyboard import Key, Listener

from ..async_ext import run_sync
from ..event_bus import EventTopic
from .hievent import HIEvent, HISource, HIType

class KeyboardListener:
    '''
    Keyboard listener based on pynput and designed
    to publish key events to an event bus
    '''

    SOURCE = HISource.KEYBOARD # pylint: disable=unused-private-member
    MAPPING = {
        Key.up: HIType.UP,
        Key.down: HIType.DOWN,
        Key.left: HIType.LEFT,
        Key.right: HIType.RIGHT,
        'z': HIType.SELECT0,
        'x': HIType.SELECT1,
        Key.esc: HIType.POWER,
    }

    def __init__(self, event_bus: EventTopic):
        self.__event_bus = event_bus
        self.__active_keys = set()
        self.__listener = Listener(
            on_press=self.__on_press,
            on_release=self.__on_release)

    def start(self):
        '''
        Start listening for keyboard events
        '''
        self.__listener.start()

    def stop(self):
        '''
        Stop listening for keyboard events
        '''
        self.__listener.stop()

    @classmethod
    def __key_to_hitype(cls, key: Key) -> HIType:
        try:
            return cls.MAPPING[key]
        except KeyError:
            return HIType.UNKOWN

    def __on_press(self, key: Key):
        action = None
        if key in self.__active_keys:
            action = 'repeated'
        else:
            self.__active_keys.add(key)
            action = 'pressed'
        hitype = self.__key_to_hitype(key)
        event = HIEvent(self.SOURCE, hitype, {'action' : action})
        task = self.__event_bus.publish(event)
        print("press")
        run_sync(task)

    def __on_release(self, key: Key):
        if key in self.__active_keys:
            self.__active_keys.remove(key)
        hitype = self.__key_to_hitype(key)
        event = HIEvent(self.SOURCE, hitype, {'action' : 'release'})
        task = self.__event_bus.publish(event)
        print("release")
        run_sync(task)
