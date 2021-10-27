Amazon Pay Payment Acquirer
===========================

Amazon Pay makes it simple for hundreds of millions of customers around the globe to pay for products and services using the information already stored in their Amazon accounts. It’s a familiar buying experience from a brand customers know and trust.


Installation & Configuration
----------------------------

##### 1. Resolve dependencies

This module will use ["The official Amazon Pay Python SDK"](https://github.com/amzn/amazon-pay-sdk-python/) which should be installed into host system before module use.

It might be installed using PyPI, for example:
```
$ pip3 install amazon_pay
```

##### 2. Register on Amazon Pay

To configure payment acquirer module you need to perform the registration steps described [here](https://developer.amazon.com/docs/amazon-pay-onetime/register.html) for get values of:

- Merchant ID (seller ID)
- MWS Access Key and MWS Secret Key
- Client ID


##### 3. Install payment acquirer module in Odoo

##### 4. Configure Amazon Pay Payment Acquirer

Go to payment acquirer configuration form and set value of _Merchant ID_, _MWS Access Key_, _MWS Secret Key_ and _Client ID_.

You should also define correct **Region** value. It is important for load correct Amazon Widgets scripts (Amazon will display runtime error if region incorrect). So, if you not sure with your region value - try to set **NA** region (this is default value).

There is an additional option on payment acquirer form which should be explained:

> If option named *"Close order reference after capture"* is checked, then Amazon order reference will be closed after authorization will be captured. Normally, this option should be always TRUE (see [this](https://developer.amazon.com/docs/amazon-pay-onetime/mark-order-as-closed.html) for details).

Keep in mind, as Amazon says, the **best practice recommendation**: all API calls should be submitted to the Sandbox for test purposes before being moved live to your production systems.


Key points of usage
-------------------

Amazon Pay supports separate authorization feature, so you can set option _"Capture Amount Manually"_ to TRUE for capture (or void) transactions manually.

Also you should know that module store all communication information about requests to Amazon Pay (and responses) per each transaction. You can see this information table in developer mode on transaction form (of course if you have administrative rights).


Limitations
-----------

- This module provides one-time only payments functionality with Amazon Pay without recurring payments.

- Only synchronous Authorization API calls supported now (you can see [this one](https://developer.amazon.com/docs/amazon-pay-onetime/request-an-authorization.html) for details).

- Handling Instant Payment Notification ([IPN](https://developer.amazon.com/docs/amazon-pay-onetime/handling-ipn.html)) messages not yet implemented.

