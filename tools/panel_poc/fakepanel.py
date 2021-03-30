''' POC for display panel '''

import asyncio
import sys
from tkinter import * # pylint: disable=unused-wildcard-import,wildcard-import
from PIL import ImageFilter, ImageTk, Image

class FakePanel(Tk):
    """
    Fake panel POC
    """

    def __init__(self, path, refresh_rate=1/60):
        super().__init__()
        self.destroyed = False
        self.title('xHoundPi fake panel')
        self.refresh_rate = refresh_rate # in secs
        self._init()
        self._setup_canvas(path)

    async def mainloop_async(self):
        """
        Run the main update loop async
        """
        while not self.destroyed:
            try:
                await self._update_async()
            except TclError as ex:
                self.destroyed = str(ex).endswith('application has been destroyed')

    async def _update_async(self):
        self.update()
        await asyncio.sleep(self.refresh_rate)

    def _init(self):
        if sys.platform == 'win32':
            self._win_init()
        else:
            self._linux_init()

    def _win_init(self):
        #self.wm_attributes('-type', 'splash')
        pass

    def _linux_init(self):
        self.attributes('-type', 'dock')

    def _setup_canvas(self, path):
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.original = Image.open(path).convert('RGB')
        self.geometry(f'{self.original.width*4}x{self.original.height*4}')
        self.image = ImageTk.PhotoImage(self.original)
        self.display = Canvas(self, bd=0, highlightthickness=0)
        self.display.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")
        self.display.grid(row=0, sticky=W+E+N+S)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        size = (event.width, event.height)
        resized = self.original.resize(size,Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")