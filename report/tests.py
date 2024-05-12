from audioop import reverse
from unittest import TestCase

from users.models import User


class PDFReportTest(TestCase):
    def setUp(self):
        self.client = User()
        self.user = User.objects.create_user(username='testuser')

    def test_generate_pdf_report(self):
        url = reverse('generate_pdf_report', kwargs={'category': 'login'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(b'Analytics Report for login', response.content)
        self.assertIn(b'testuser', response.content)
        self.assertIn(b'login', response.content)
