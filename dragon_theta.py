import sys

import pygame

import theta

theta.set_default_data_path()
game = theta.Game(120)
sfx = theta.sfx.SFXManager()
anims = theta.animation.AnimationManager()

game.set_name("The Dragon")
game.set_icon("./data/icon.png")
game.camera.set_background((220, 120, 62))

dragon = anims.create_entity(
    game.camera.display.get_width() - 78,
    3 * game.camera.display.get_height() // 4 - 96,
    54,
    96,
    "dragon",
    game,
)
# TODO: get level in game, work on `Modifier` class for anims (change colour based on hp)
player = anims.create_entity(
    30, 3 * game.camera.display.get_height() // 4 - 96, 54, 96, "player", game
)

while True:

    for event in game.input.get():
        match event.type:
            case theta.input.QUIT:
                pygame.quit()
                sys.exit()
            case theta.input.KEYDOWN2:
                match event.key:
                    case theta.input.ESCAPE:
                        pygame.quit()
                        sys.exit()

    game.update()
