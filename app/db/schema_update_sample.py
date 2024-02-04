from app.models.post_models import FacebookPost, CommentsOfPosts, SubComments

def get_sub_comments(comment) -> dict:
    return SubComments( 
        id=str(comment['id']),
        sub_comment=str(comment['sub_comment']),
        created_time=str(comment['created_time'])
    )

def get_comments_of_post(comment) -> dict:
    return CommentsOfPosts( 
        id=str(comment['id']),
        comment=str(comment['comment']),
        created_time=str(comment['created_time']),
        likes=int(comment['likes']),
        sub_comments=[get_sub_comments(sub_comment) for sub_comment in comment.get('sub_comments', [])]
    )

def get_post(post) -> dict:
    return FacebookPost(
        id=str(post['id']),
        message=str(post['message']),
        created_time=str(post['created_time']),
        likes=int(post['likes']),
        comments=[get_comments_of_post(comment) for comment in post.get('comments', [])]
    )

def list_posts(posts) -> list:
    return [get_post(post) for post in posts]