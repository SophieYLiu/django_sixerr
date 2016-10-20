from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Gig, Profile, Purchase, Review
from .forms import GigForm
from twilio.rest import TwilioRestClient


import braintree

braintree.Configuration.configure(braintree.Environment.Sandbox,
									merchant_id="7f36yb4sb7v7x3vk",
									public_key="j9fxrnkcc7xtfb86",
									private_key="9f39d9bba752162ea348002871a3f16c"
)

# Create your views here.
def home(request):
	gigs = Gig.objects.filter(status=True)
	return render(request, 'home.html', {"gigs": gigs})

def gig_detail(request, id):
	if request.method == 'POST' and \
		not request.user.is_anonymous() and \
		Purchase.objects.filter(gig_id=id, buyer=request.user).count() > 0 and \
		'content' in request.POST and \
		request.POST['content'].strip() != '':
		Review.objects.create(content=request.POST['content'], gig_id=id, user=request.user)

	try:
		gig = Gig.objects.get(id=id)
	except Gig.DoesNotExist:
		return redirect('/')

	if request.user.is_anonymous() or \
		Purchase.objects.filter(gig=gig, buyer=request.user).count() == 0 or \
		Review.objects.filter(gig=gig, user=request.user).count() > 0:
		show_post_review = False
	else:
		show_post_review = Purchase.objects.filter(gig=gig, buyer=request.user).count() > 0

	reviews = Review.objects.filter(gig=gig)
	client_token = braintree.ClientToken.generate()
	return render(request, 'gig_detail.html', {"show_post_review": show_post_review, "reviews": reviews, "gig": gig, "client_token": client_token})

@login_required(login_url="/")
def create_gig(request):
	error = ''
	if request.method == 'POST':
		gig_form = GigForm(request.POST, request.FILES)
		if gig_form.is_valid():
			gig = gig_form.save(commit=False)
			gig.user = request.user
			gig.save()
			return redirect('my_gigs')
		else:
			error = "Data is not valid"
	

	gig_form = GigForm()
	return render(request, 'create_gig.html', {
		"error": error})

@login_required(login_url="/")
def edit_gig(request, id):
	try:
		gig = Gig.objects.get(id=id, user=request.user)
		error = ''
		if request.method == 'POST':
			gig_form = GigForm(request.POST, request.FILES, instance=gig)
			if gig_form.is_valid():
				gig.save()
				return redirect('my_gigs')
			else:
				error = "Data is not valid"
		return render(request, 'edit_gig.html', {"gig": gig, "error": error})
	except Gig.DoesNotExist:
		return redirect('/')


@login_required(login_url="/")
def my_gigs(request):
	gigs = Gig.objects.filter(user=request.user)
	return render(request, 'my_gigs.html', {"gigs": gigs})


def profile(request, username):
	if request.method == 'POST':
		profile = Profile.objects.get(user=request.user)
		profile.about = request.POST['about']
		profile.slogan = request.POST['slogan']
		profile.save()
	else:
		try:
			profile = Profile.objects.get(user__username=username)
		except Profile.DoesNotExist:
			return redirect('/')


	gigs = Gig.objects.filter(user=profile.user, status=True)
	return render(request, 'profile.html', {"profile": profile, "gigs": gigs})

@login_required(login_url="/")
def create_purchase(request):
	if request.method == 'POST':
		try:
			gig = Gig.objects.get(id = request.POST['gig_id'])
		except Gig.DoesNotExist:
			return redirect('/')

		nonce = request.POST["payment_method_nonce"]
		result = braintree.Transaction.sale({
				"amount": gig.price,
				"payment_method_nonce": nonce	
			})

		if result.is_success:

			message = 'Shit David'
			from_ = '+12015604123'
			to = '+16265860724';
			client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
			# account = "AC158a6a78c3d572b3535b317437e5a10d"
			# token = "afa5fa7609fd94abf1de22a447aebda5"
			# client = TwilioRestClient(account, token)
			response = client.messages.create(body=message, to=to, from_=from_)

			# Purchase.objects.create(gig=gig, buyer=request.user)
			# account = "AC158a6a78c3d572b3535b317437e5a10d"
			# token = "afa5fa7609fd94abf1de22a447aebda5"
			# client = TwilioRestClient(account, token)

			# message = client.sms.messages.create(to="+16265860724",
			#                                      from_="+12015604123",
			#                                      body="Hi this is green onion")
			

			
	return redirect('/')


@login_required(login_url="/")
def my_sellings(request):
	purchases = Purchase.objects.filter(gig__user=request.user)
	return render(request, 'my_sellings.html', {"purchases": purchases})


@login_required(login_url="/")
def my_buyings(request):
	purchases = Purchase.objects.filter(buyer=request.user)
	return render(request, 'my_buyings.html', {"purchases": purchases})


def category(request, link):
	categories = {
		"graphics-design": "GD",
		"digital-marketing": "DM",
		"video-animation": "VA",
		"music-audio": "MA",
		"programming-tech": "PT"
	}
	try:
		gigs = Gig.objects.filter(category=categories[link])
		return render(request, 'home.html', {"gigs": gigs})
	except KeyError:
		return redirect('home')

def search(request):
	gigs = Gig.objects.filter(title__contains=request.GET['title'])
	return render(request, 'home.html', {"gigs": gigs})

