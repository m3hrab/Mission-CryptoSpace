import pygame

def wrap_text(surface, text, font, color, rect):
    """Wraps text within a rectangle, returns final y-coordinate."""
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() <= rect.width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    y = rect.y
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, y))
        y += font.get_height() + 5
    return y