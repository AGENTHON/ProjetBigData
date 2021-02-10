import boto3
import initEc2Instance
import initQueues

# Create requestQueue and responseQueue
requestQueue, responseQueue = initQueues.initQueues()

# Create EC2 instance (with key-pair ans security group)
# Install all necessary packages
# Send EC2 worker's python files on instance
# Run EC2 worker on instance
initialization = input("Initialize the instance ?:(y/n) ")
if (initialization=='y'):
     initEc2Instance.initInstance()

print()
print()
print()

# Client part
# This script ask some integers from console to user. Ex : 78 65 12 32
# Then it parse those integers and format them in new string like : "78/65/12/32"
# Finally it send this string in queue created before
myInput = input("Enter integers (separate by space): ")    # Ask integer to user
fields = myInput.split(" ")             # Split integers by space

integers = []                                           # Parse integers from string
for field in fields:                                    #
    try:                                                #
        i = int(field)                                  #
        integers.append(i)                              #
    except ValueError:                                  #
        print("'"+field+"' is not a valid integer")     #

print("Valid Integers are = "+str(integers))

string = ""                                             # Build string that will be sent to queue
for integer in integers:                                # ex : '78/23/56'
    string = string + str(integer) + "/"                #
string = string[:-1]                                    #

print("Sending='"+string+"'")
response = requestQueue.send_message(MessageBody=string, MessageGroupId='messages')



#
# Get and display response message from responseQueue
#
print()
print("Waiting for results ...")
print()
not_received = True
while not_received :
# Process messages by printing out body and optional author name
    for message in responseQueue.receive_messages(MessageAttributeNames=['Author']):
    # Get the custom author message attribute if it was set
        author_text = ''
        if message.message_attributes is not None:
            author_name = message.message_attributes.get('Author').get('StringValue')
            if author_name:
                author_text = ' ({0})'.format(author_name)

        #calcul du resultat
        print(message.body)
        not_received = False

        message.delete()