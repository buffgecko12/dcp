from django.test import TestCase

from django.contrib.auth import authenticate, get_user_model

class CreateUserTests(TestCase):

    def create_user(self):
            
        # Create new user
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', 
            usertype = 'ST', 
            firstname = 'Test', 
            lastname = 'Orama',
            username = 'buffgecko',
            emailaddress = 'fart@poop.com'
        )
            
        self.assertIs(newuser, True)

'''            
    def test_future_question(self):
        # Check that detail view of future test returns a 404 not found message
        url = reverse('polls:detail', args=(10))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self.assertIs(True, True)
        self.assertQuerysetEqual(response.context['latest_question_list'],[])
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

'''