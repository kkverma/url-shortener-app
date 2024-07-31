import aws_cdk as core
import aws_cdk.assertions as assertions

from url_shortener_app.url_shortener_app_stack import UrlShortenerAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in url_shortener_app/url_shortener_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = UrlShortenerAppStack(app, "url-shortener-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
