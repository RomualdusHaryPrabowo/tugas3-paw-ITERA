from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy import create_engine
from models import DBSession, Base, Review
import ai_services
import transaction


DB_URL = 'postgresql://postgres:12345@localhost:5432/review_db'

def add_cors(event):
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept',
        })
    event.request.add_response_callback(cors_headers)

@view_config(route_name='analyze', renderer='json', request_method='POST')
def analyze_view(request):
    try:
        payload = request.json_body
        text = payload.get('text', '')
        if not text: return {'error': 'Text kosong'}

   
        sentiment = ai_services.analyze_sentiment(text)
        points = ai_services.extract_key_points(text)

     
        new_review = Review(text=text, sentiment_label=sentiment['label'], 
                          sentiment_score=sentiment['score'], key_points=points)
        DBSession.add(new_review)
        DBSession.flush()
        data = new_review.to_json()
        transaction.commit()
        return data
    except Exception as e:
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='get_reviews', renderer='json', request_method='GET')
def get_reviews_view(request):
    reviews = DBSession.query(Review).order_by(Review.created_at.desc()).all()
    return [r.to_json() for r in reviews]

@view_config(route_name='analyze', request_method='OPTIONS')
@view_config(route_name='get_reviews', request_method='OPTIONS')
def options_view(request):
    return Response(status=200)

if __name__ == '__main__':
    engine = create_engine(DB_URL)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with Configurator() as config:
        config.add_subscriber(add_cors, 'pyramid.events.NewRequest')
        config.add_route('analyze', '/api/analyze-review')
        config.add_route('get_reviews', '/api/reviews')
        config.scan()
        app = config.make_wsgi_app()
    print("SERVER ON: http://localhost:6543")
    from waitress import serve
    serve(app, host='0.0.0.0', port=6543)