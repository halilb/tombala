Tombala Game
===========================

# INSTRUCTIONS

* Clone this repo.
* Run *python server/main.py* to run the server.
* Run *python client/main.py* to run the client.
* /login {username} to set user name.
* /create {roomname} {countdown} to create a new room. Game will start after {countdown} seconds.
* /join {roomname} to join a game.
* /rooms to display existing rooms.
* /quit to quit a game.
* /mark {number} if you have the number in your playcard.
* /cinko {total} to announce your new cinko.
* Click *Next Number* button to request new number. A new number will be distributed when all users in the room declare they are ready.

# PROTOCOL

*Tombola* is a board game originated in Italy. In Turkey, it is called *Tombala* and traditionally played in new year's eve. It's similar to *bingo* game.

![Tombala game card image](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Tombola.jpg/320px-Tombola.jpg)

This document defines functional requirements for a simple tombala game and offers a simple text-based protocol desing which will be used for communication between Tombala Clients and Tombala Server. The protocol is designed to run on top of the TCP.

This protocol is designed to support multiple *tombala* sessions simultaneously.

# 1. Functional Requirements

#### 1.1. Client-Server Connection

User connects to the Tombala Server through any Tombala Client by providing a user name. User name shall be unique across the Tombala server.

User shall be removed from all games when he loses internet connection. Timeout shall be 30 seconds.

#### 1.2. Game Rooms

##### 1.2.1. Creating a game room

The system shall support multiple games simultaneously.

Every user shall be able to create a new game room. User shall provide a countdown value to arrange start date of the game. Game starts after coundown interval ends.

##### 1.2.2. Displaying game rooms

User shall display existing rooms.

##### 1.2.3. Joining a game room

User shall join a game room by providing the room's name.
User shall receive an error:
* If the game has already started.
* If user is already in another game room.

##### 1.2.4. Quiting a game room

User shall quit a game room before the game finishes. He can then join any other game if the game is not started.

#### 1.3. The Game

A game card contains three rows and five numbers on each row. It is randomly generated and distributed when the game starts.

A new number should be randomly generated distributed when all users want to proceed to the next turn. This number should be between 1 and 90. User checks whether he has the number for the current turn and proceeds. The game should be on hold until all users proceed to the next turn.

When a user marks every number in a row of the game card, he should announce it as *cinko*. This claim must be validated and distributed to the other users. Users are responsible for following the numbers and announcing cinkos. Game is over when a user achieves three *cinkos*.


# 2. MESSAGE FORMAT

All protocol messages have to contain a keyword which describes the type of the message. This keyword will be called as the header of the message.

Protocol messages contain body field as the content. The format of the body message is Javascript Object Notation(JSON). You can find JSON format documentation here: http://json.org/

Header keyword and and body message is seperated with a colon character.

    {HEADER_KEYWORD}:{BODY_MESSAGE}

There are two general types of communication:

1. After user actions, client issues a request with relevant header and server responses with an error or success header.

2. When state changes on the server, it broadcasts messages to related clients.

All messages shall close with a line break character \n.

## 2.1. Client Request Format

Tombala clients are responsible for adding a request identifier to the body message. The identifier is added to the response body by the server, and client uses that to correspond server responses with the relavant request. The identifier will be called as sequence number.

Sequence numbers are integers generated on the client side. They are not manipulated but simply echoed in responses.

**Client Request Types**

- CHBEAT: Client Heartbeat
- CLOGIN: Client Login
- CCROOM: Client Create Room
- CLROOM: Client List Rooms
- CJROOM: Client Join Room
- CQROOM: Client Quit Room
- CCINKO: Client Cinko
- CNNMBR: Client Next Number

**Server Response Types for Client Requests**

- SSUCCS: Server response with success
- SERROR: Server response with error

## 2.2. Server Broadcast Format

Server broadcasts messages about a room to the connected clients when state changes for the room.

- BGCARD: Broadcast Game Card
- BNUMBR: Broadcast New Number
- BCINKO: Broadcast Cinko
- BUSRLS: Broadcast User List

# 3.1. Client Requests

#### CHBEAT : Client Heartbeat

Client heartbeat message is just used to inform the server that the client is still connected.

*CHBEAT* messages are expected to be sent regularly while the client is online. Expected interval time is 10 seconds. Client will be considered as disconnected when there is no heartbeat in the last 30 seconds. Disconnected clients will be removed from their active tombala rooms and game continues in those rooms.

Example Request:

    CHBEAT:{
        "seq": 111
    }

Example Response:

    SSUCCS:{
        "seq": 111
    }

#### CLOGIN: Client Login

*CLOGIN* is used to set a username for client connection. This request is needed to authenticate the client on the server and it must be issued before any other request.

Request fields:

- **username**(string): It should be unique across the system.

Example request:

    CLOGIN:{
        "seq": 111,
        "username": "user1"
    }

Expected responses: SSUCCS, SERROR

Expected response fields:

- **message**(string): Description text for SSUCCS or SERROR

Success response example:

    SSUCCS:{
        "seq": 111,
        "message": "Welcome user1!"
    }

Error response example:

    SERROR:{
        "seq": 111,
        "message": "user1 already exists on the system. Please choose another username!"
    }

#### CCROOM: Client Create Room

*CCROOM* is used to create a new game room.

Request fields:

- **roomname**(*string*): An alias for the tombala session room. It needs to be unique across the system.
- **countdown**(*integer*) : This parameter should be defined as seconds. It is used to calculate the starting date of the game. 

Example request:

    CCROOM:{
        "seq": 111,
        "roomname": "room1",
        "countdown": 120 // 2 minutes
    }

Expected responses: SSUCCS, SERROR

Expected response fields:

- **message**(*string*): Description text for SSUCCS or SERROR

Success response example:

    SSUCCS:{
        "seq": 111,
        "message": "room1 is created!"
    }

Error response example:

    SERROR:{
        "seq": 111,
        "message": "room1 already exists!"
    }
    
    
    
#### CLROOM: Client List Rooms
 
*CLROOM* is used to retrieve existing game rooms.

This request does not need additional body parameters.

Example request:

    CLROOM:{
        "seq": 111
    }

Expected response: SSUCCS

Expected response fields:

* **rooms**(*array*): This field contains a collection with Room objects.
* **room.roomname**(*string*): Alias for the room.
* **room.startTime**(*date*): Starting date of the game. It is defined in seconds.
* **room.userlist**(*array*): Contains user names of current users in the room.

Response example:

    SSUCCS:{
        "seq": 111,
        "rooms": [{
        	"roomname": "room1",
            "startTime": "2016-01-10 19:22:51.899637",
            "userlist": ["user1", "user2"]
        }, {
            "roomname": "room2",
            "startTime": "2016-01-10 19:23:51.899637"
            "userlist": ["user3", "user4"]
        }]
    }
    
#### CJROOM: Client Join Room

*CJROOM* is used to join a game room.

Clients can not join a room if they are already in another room. For such scenarios, *CQROOM* request must be issued before *CJROOM*.

Request fields:

- **roomname**(*string*): Room name.

Example request:

    CJROOM:{
        "seq": 111,
        "roomname": "room1"
    }

Expected responses: SSUCCS, SERROR

Expected response fields:

- **message**(*string*): Description text for SSUCCS or SERROR

Success response example:

    SSUCCS:{
        "seq": 111,
        "message": "Joined room1 successfully!"
    }

Error response example:

    SERROR:{
        "seq": 111,
        "message": "room1 does not exist!"
    }
    
#### CQROOM: Client Quit Room

*CQROOM* is used to quit from user's current game room.

Example request:

    CQROOM:{
        "seq": 111,
    }

Expected responses: SSUCCS, SERROR

Expected response fields:

- **message**(*string*): Description text for SSUCCS or SERROR

Success response example:

    SSUCCS:{
        "seq": 111,
        "message": "You've left room1 successfully!"
    }

Error response example:

    SERROR:{
        "seq": 111,
        "message": "You already aren't in a room currently!"
    }
    
#### CCINKO: Client Cinko

CCINKO is used announce cinko. Server validates client's cinko claim and broadcasts it to all connected clients in the room.

This request takes a **total** parameter in the body. The game is over when a client has three cinkos.

Request fields:

- **total**(*integer*): Total cinko count. Minimum 1, maximum 3.

Example request:

    CCINKO:{
        "seq": 111,
        "cinko": 3 // wins the game
    }

Expected responses: SSUCCS, SERROR

Expected response fields:

- **message**(*string*): Description text for SSUCCS or SERROR

Success response example:

    SSUCCS:{
        "seq": 111,
        "message": "Congratulations!"
    }

Error response example:

    SERROR:{
        "seq": 111,
        "message": "Your cinko claim is wrong!"
    }
    
#### CNNMBR: Client Next Number

*CNNMBR* is used to inform server that the client is ready for a new number. It is client's responbisility to check his game card after receiving a new number. After checking the game card, clients have to issue *CNNMBR* request. Game will not proceed until all participating users send a *CNNMBR* request.

Example request:

    CNNMBR:{
        "seq": 111
    }

Expected responses: SSUCCS, SERROR

Expected response fields:

- **message**(*string*): Description text for SSUCCS or SERROR

Success response example:

    SSUCCS:{
        "seq": 111,
        "message": "Next number will be broadcasted when everyone proceeds!"
    }

Error response example:

    SERROR:{
        "seq": 111,
        "message": "You've already proceeded for the current turn!"
    }
    
# 3.2. Server Broadcasts

Broadcast messages are issued from server when the room's state changes. Clients are subscribed to those broadcast messages when they join the room.

#### BGCARD: Broadcast Game Card

This message is broadcasted when the game starts in the room.

Message fields:

- **gamecard**(*array*): It has three rows represeting rows in an actual game card.
- **gamecard.row**(*array*): Every row has five integer numbers between 1 and 90. Clients shall use this field to determine cinkos. 

Example message:

    BGCARD:{
        "gamecard": [
          [[77, 1, 18, 4, 43],
          [6s1, 27, 25, 16, 56],
          [46, 80, 31, 73, 45]]
        ]
    }
    
#### BNUMBR: Broadcast New Number

*BNUMBR* is broadcasted when a new number is generated on the server for a new turn.

Message fields:

- **number**(*integer*): A random number generated on the server. Minimum 1, maximum 90. Generated numbers must be unique for any given game session. Clients use this number to mark their game cards. Clients have to issue *CNEXT* request using this number as a parameter for proceeding to next turn.

Example message:

    BNUMBR:{
        "number": 66
    }
    
#### BCINKO: Broadcast Cinko

*BCINKO* is broadcasted when a user achieves a new cinko. A game is over when any user has three cinkos. Clients shall use this information to let the user know when the game is over.

Message fields:

- **username**(*string*): Username for the new cinko's owner.
- **total**(*integer*): User's total cinko count with the new cinko. Minimum 1, maximum 3. User wins the game when it is 3.

Example message:

    BCINKO:{
        "username": "user1",
        "total": 3 // user1 wins the game
    }
    
#### BUSRLS: Broadcast User List

*BUSRLS* broadcasts user list for the current room. It is broadcasted every time a new user attends or leaves the game. It is client's responsibility to check differences in the list to determine incoming or leaving users.

Message fields:

- **userlist**(*array*): A collection for usernames.

Example message:

    BUSRLS:{
        "userlist": ["user1", "user2", "user4"]
    }
