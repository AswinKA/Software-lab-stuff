Advanced college of Engineering

& Management

Lab No:1

Name:Aswin Singh KarkiDepartment of

Roll no: ACE080BCT016Computer and Electronics Engineering

Crop Information

and

Disease Detection Management system

Problem Statement

Many new farmers face difficulties in crops selection and crops treatment and with lack of information due to no a reliable platform about crop diseases, irrigation requirements, and cultivation practices. Farmers often rely on traditional methods or personal experience, or word of mouth sources of information, which may not always be reliable or up to date.

Crop diseases can spread rapidly if not identified and treated quickly stage, leading to reduced yields and financial losses. Farmers also struggle to access timely recommendations regarding crop care, disease prevention for different crop varieties.

As a result of this, agricultural productivity is often reduced, operational costs increase, and farmers face challenges in making informed decisions about crop management.

Proposed Solution

Crops info and disease detection management system is designed to create a centralized info platform which will have all info about the crops. Info like scientific name, common name, diseases and its prevention and treatment. It will include photo of healthy plant along with different photo of infected photos so farmers can identify based on looks too. It can have info on fertilizers to use, treatment plan, damage mitigation. This will give farmer clear risks and profits on every crops.

Example if a plant has non treatable disease, farmer can be prepared before hand to destroy all infected crops to save healthy ones. This will increase the yield and minimize or in some case completely remove loss.

SOFTWARE REQUIREMENT SPECIFICATION (SRS) FUNCTIONAL REQUIREMENTS

#Admin function

R1:Login_user

Description:Admin should be able to login to the system Input:Email address and password

Output: Successful login or login failure message.

Process: The system verifies the credentials and grants access to authorized users

R2:Upload _images

Description:Admin should be able to post and remove images Input: Image s like jpg, png format

Output: Upload successful or Unsuccessful

Process: System validate the file and stores it in on the respective crop

R3:Addition_info

Description: It should contain info like scientific name, common name and medicinal benefit if any.

Input: Some info should be displayed under the image

Output: A clear info on the crops under the image of respective crop

Process: The system display the addition info under the image

R4:Catogory

Description:A collapse-able section which extends to show more info like disease, etc.

Input:Adding info diseases and has separate category for each disease Output:A extendable and collapse-able info separated by category Process: The system categorize separates info based on disease

R5:Ban_user

Description:Admin can ban users which spread miss-info or break ToS Input: Lock user access

Output: Baned Message

Process: The system restricts access to the site and viewing privileges

#User Function

R1:Register_user

Description: User should be able to register to the system using their credentials.

Input: E-mail, password, etc

Output: Show successful registration or unsuccessful registration

Process: The system validates the information, generates a unique user ID, creates an account, and grants access to the system

R1:Login_user

Description:User should be able to log in to the system using their credentials Input: Email address and password.

Output: Successful login or login failure message

Process: The system verifies the credentials and grants access to authorized users.

R2:Comment_section

Description: User should be able to ask or add info via comments Input:User message

Output:Display Message

Process:The system should check if the comment is breaking ToS and remove message if ToS is broken

R3:Direct_message

Input:receiver and Sender Private message

Output: show notification and Display message only to receiver

Process:The system should show the message to only receiver and the sender

NON-FUNCTIONAL REQUIREMENTS

R1: Performance

Description: The system should respond quickly to user requests.

Input: User requests.

Output: Fast system response.

Process: The system processes requests efficiently.

R2: Security

Description: User accounts and data should be protected from unauthorized access.

Input: User credentials and system data.

Output: Secure access to the system.

Process: Passwords are encrypted and access is controlled through authentication.

R3: Reliability

Description: The system should operate correctly without frequent failures.

Input: System operations.

Output: Consistent and dependable service.

Process: The system maintains data integrity and recovers from failures.

R4: Availability

Description: The system should be accessible whenever users need it.

Input: User access requests.

Output: Continuous system availability.

Process: The server remains operational except during scheduled maintenance.

R5: Usability

Description: The system interface should be easy to understand and use.

Input: User interactions.

Output: User-friendly navigation and information access.

Process: Information is organized clearly using categories and expandable sections.

R6: Maintainability

Description: The system should be easy to update and maintain.

Input: Administrative updates and modifications.

Output: Updated system content and features.

Process: Administrators can modify crop and disease information without affecting system operation.

CONSTRAINTS

Technology Constraint: The system must be implemented using approved web technologies and a relational database.

Browser Constraint: The system must support modern web browsers such as Chrome, Firefox, Edge, and Safari.

Image Format Constraint: Only JPG, JPEG, and PNG image formats must be accepted.

Authentication Constraint: Only registered users is allowed to comment or send direct messages.

Internet Constraint: Users must have an active internet connection to access the system.

Storage Constraint: Image uploads and stored information are limited by available server storage capacity.

Content Constraint: All crop and disease information must be manually entered and maintained by administrators.

Usecase Diagram

Class Diagram