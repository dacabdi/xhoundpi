import asyncio
import numpy as np
import pygame

async def render():
    def sin2d(x,y):
        """2-d sine function to plot"""

        return np.sin(x) + np.cos(y)

    def getFrame():
        """Generate next frame of simulation as numpy array"""

        # Create data on first call only
        if getFrame.z is None:
            xx, yy = np.meshgrid(np.linspace(0,2*np.pi,h), np.linspace(0,2*np.pi,w))
            getFrame.z = sin2d(xx, yy)
            getFrame.z = 255*getFrame.z/getFrame.z.max()

        # Just roll data for subsequent calls
        getFrame.z = np.roll(getFrame.z,(1,2),(0,1))
        return getFrame.z

    h,w=480,640
    border=50
    N=0
    getFrame.z = None

    pygame.init()
    screen = pygame.display.set_mode((w+(2*border), h+(2*border)))
    pygame.display.set_caption("Serious Work - not games")
    done = False
    clock = pygame.time.Clock()

    # Get a font for rendering the frame number
    basicfont = pygame.font.SysFont(None, 32)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Clear screen to white before drawing
        screen.fill((255, 255, 255))

        # Get a numpy array to display from the simulation
        npimage=getFrame()

        # Convert to a surface and splat onto screen offset by border width and height
        surface = pygame.surfarray.make_surface(npimage)
        screen.blit(surface, (border, border))

        # Display and update frame counter
        text = basicfont.render('Frame: ' + str(N), True, (255, 0, 0), (255, 255, 255))
        screen.blit(text, (border,h+border))
        N = N + 1

        pygame.display.flip()
        await asyncio.sleep(1/120)
