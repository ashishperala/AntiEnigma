from django.contrib import messages
from django.shortcuts import redirect, render
import PIL
from PIL import Image
from django.contrib.auth.models import User, auth
# Create your views here.
def register(request):
    if request.method == 'POST' :
        if request.POST.get('username2','')=='':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            email = request.POST['email']
            if password1==password2:
                if User.objects.filter(username=username).exists():
                    messages.info(request,'Username already exists!!')
                    return redirect('register')
                elif User.objects.filter(email=email).exists():
                    messages.info(request,'email taken!!')
                    return redirect('register')
                else:
                    user= User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                    user.save();
                    return redirect('upload')
            else:
                messages.info(request,'passwords doesnt match')
                return redirect('register')
        else:
            username = request.POST['username2']
            password3 = request.POST['password3']
            #password3 = request.POST.get('password3', 'default value')
            user = auth.authenticate(username=username, password=password3)
            if user is not None:
                auth.login(request,user)
                return redirect('upload')
            else:
                messages.info(request,'invalid credentials')
                return redirect('register')   
    else:
        return render(request, 'login.html')


def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        print(type(uploaded_file))
        print(uploaded_file.name)
        print(uploaded_file.size)
        img=uploaded_file.name
        print(type(img))
        #image = Image.open(img, 'r')
        image = Image.open(r"C:\Users\KITTU\steg2.png")
        data = ''
        imgdata = iter(image.getdata())
        while (True):
            pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] +imgdata.__next__()[:3]]
            # string of binary data
            print('adasfk')
            binstr = ''
            for i in pixels[:8]:
                if (i % 2 == 0):
                    binstr += '0'
                else:
                    binstr += '1'
            data += chr(int(binstr, 2))
            if (pixels[-1] % 2 != 0):
                messages.info(request,data)
                return redirect('upload')
               # return data
    else:
        return render(request, 'upload.html')
# PIL module is used to extract
# pixels of image and modify it

# Convert encoding data into 8-bit binary
# form using ASCII value of characters
def genData(data):

		# list of binary codes
		# of given data
		newd = []

		for i in data:
			newd.append(format(ord(i), '08b'))
		return newd

# Pixels are modified according to the
# 8-bit binary data and finally returned
def modPix(pix, data):

	datalist = genData(data)
	lendata = len(datalist)
	imdata = iter(pix)

	for i in range(lendata):

		# Extracting 3 pixels at a time
		pix = [value for value in imdata.__next__()[:3] +
								imdata.__next__()[:3] +
								imdata.__next__()[:3]]

		# Pixel value should be made
		# odd for 1 and even for 0
		for j in range(0, 8):
			if (datalist[i][j] == '0' and pix[j]% 2 != 0):
				pix[j] -= 1

			elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
				if(pix[j] != 0):
					pix[j] -= 1
				else:
					pix[j] += 1
				# pix[j] -= 1

		# Eighth pixel of every set tells
		# whether to stop ot read further.
		# 0 means keep reading; 1 means thec
		# message is over.
		if (i == lendata - 1):
			if (pix[-1] % 2 == 0):
				if(pix[-1] != 0):
					pix[-1] -= 1
				else:
					pix[-1] += 1

		else:
			if (pix[-1] % 2 != 0):
				pix[-1] -= 1

		pix = tuple(pix)
		yield pix[0:3]
		yield pix[3:6]
		yield pix[6:9]

def encode_enc(newimg, data):
	w = newimg.size[0]
	(x, y) = (0, 0)

	for pixel in modPix(newimg.getdata(), data):

		# Putting modified pixels in the new image
		newimg.putpixel((x, y), pixel)
		if (x == w - 1):
			x = 0
			y += 1
		else:
			x += 1