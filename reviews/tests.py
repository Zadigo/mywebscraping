from django.test import Client, RequestFactory, TestCase
from reviews.api import views

EXAMPLE_DATA = {
    'name': 'Paul Point du Jour',
    'url': 'https://www.google.com/maps/search/boulangerie+paul+lyon/@50.6475457,3.0751394,12z/data=!3m1!4b1?entry=ttu',
    'feed_url': 'https://www.google.com/maps/place/Paul+Point+du+Jour/data=!4m7!3m6!1s0x47f4eb9aa525b96b:0xd466b71b3bc67789!8m2!3d45.7566226!4d4.7969463!16s%2Fg%2F1td5whrr!19sChIJa7klpZrr9EcRiXfGOxu3ZtQ?authuser=0&hl=fr&rclk=1',
    'address': '2 Rue des Aqueducs, 69005 Lyon',
    'rating': 3.3,
    'latitude': '50.6475457',
    'longitude': '3.0751394',
    'number_of_reviews': 280,
    'additional_information': '2 Rue des Aqueducs, 69005 LyonOuvert Ferme a 20:00 lundi06:30-20:00mardi06:30-20:00mercredi06:30-20:00jeudi06:30-20:00vendredi06:30-20:00samedi06:30-20:00dimanche06:30-20:00Suggerer de nouveaux horairesCommanderMenuorder.ubereats.commacarte.paul.fr04 37 41 08 53QQ4W+JQ LyonEnvoyer vers votre telephone',
    'telephone': '04 37 41 08 53',
    'website': 'https://macarte.paul.fr',
    'reviews': [
        {
            'period': 'il y a 2 semaines Nouveau',
            'rating': '5 etoiles',
            'google_review_id': 'ChdDSUhNMG9nS0VJQ0FnSURadll5Yl9RRRAB',
            'reviewer_name': 'chacon coralie',
            'reviewer_number_of_reviews': '3 avis * 1 photo',
            'text': "Je suis une cliente reguliere de Paul marius, on m'a offert un sac il y a 5 ans, je n'ai pas le ticket ni rien , quand je suis arrivee a la boutique le personnel etais accueillant et bienveillant ... Plus"
        }
    ]
}


class TestAPIEndpoint(TestCase):
    def test_bulk_create_endpoint(self):
        client = RequestFactory()
        request = client.post('google-comments/reviews/bulk', content_type='application/json', data=EXAMPLE_DATA)
        response = views.create_bulk_reviews(request)
        self.assertTrue(response.status_code == 200)
