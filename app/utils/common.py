def convert_s_score_to_color(sentiment_score):
    """
    Get color between red and green according to the sentiment score.

    Args:
        sentiment_score (float): The sentiment score between -1 and 1.

    Returns:
        str: Color code in the format '#xxxxxx'.
    """
    
    red = min(255, int((1 - sentiment_score) * 255))
    green = min(255, int((sentiment_score + 1) * 255))
    
    color_code = '#{:02x}{:02x}{:02x}'.format(red, green, 0)
    
    return color_code