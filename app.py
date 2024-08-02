#!/usr/bin/env python3
import os

import aws_cdk as cdk

from url_shortener_app.url_shortener_app_stack import UrlShortenerAppStack


app = cdk.App()
UrlShortenerAppStack(app, "UrlShortenerAppStack",
                     env=cdk.Environment(account='<AWS_ACCOUNT_ID>', region='ap-south-1'))

app.synth()
