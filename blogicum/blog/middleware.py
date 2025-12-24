class FixPostTextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        content = str(response.content, 'utf-8')
        
        content = content.replace(
            'Пост снят с публикации админом',
            'Пост не опубликован'
        )
        
        response.content = content
        
        return response