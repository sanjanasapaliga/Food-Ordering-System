from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User,UserProfile

   
    
#Creating a receiver function for signal 
#created flag will be returned when the user is created
#here user will be the sender and the function will be the receiver to create a user profile
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender,instance,created,**kwargs):
    print(created)
    if created:
        #create user profile as soon as the user is created
        UserProfile.objects.create(user=instance)
        print('Create user profile')
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the userprofile if not exist
            UserProfile.objects.create(user=instance)

# post_save.connect(post_save_create_profile_receiver,sender=User)