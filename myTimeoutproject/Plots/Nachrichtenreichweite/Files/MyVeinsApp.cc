//
// Copyright (C) 2016 David Eckhoff <david.eckhoff@fau.de>
//
// Documentation for these modules is at http://veins.car2x.org/
//
// SPDX-License-Identifier: GPL-2.0-or-later
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "veins/modules/application/traci/MyVeinsApp.h"

#include "veins/modules/application/traci/TraCIDemo11pMessage_m.h"

#include "veins/base/phyLayer/PhyToMacControlInfo.h"
#include "veins/modules/phy/DeciderResult80211.h"

using namespace veins;

Define_Module(veins::MyVeinsApp);



void MyVeinsApp::initialize(int stage)
{
    DemoBaseApplLayer::initialize(stage);
    if (stage == 0) {
        // Initializing members and pointers of your application goes heres
        msgID = 0;
        scheduledMsg = nullptr;
        hopCount = 0;
        //start = SimTime(60); //SIMTIME_M
        start = par("start");
        // to activate msg intervall see handleselfmessage function. Data collection is based on single message right now
        interval = par("interval");
        // timeout window range
        timeoutMin = par("timeoutMin");
        timeoutMax = par("timeoutMax");
        scalingDistance = par("scalingDistance");
        // based on what timeout windows should be modified
        int tmp = par("timeoutType");
        switch (tmp) {
            case 0: {
                timeoutType = NOMOD;
                break;
            }
            case 1: {
                timeoutType = DISTANCE;
                break;
            }
            case 2: {
                timeoutType = SIGNALPOWER;
                break;
            }

        }
        int tmp2 = par("distanceLock");
        switch (tmp2) {
            case 0: {
                distanceLock = NOMODIFICATION;
                break;
            }
            case 1: {
                distanceLock = FIRST25;
                break;
            }
            case 2: {
                distanceLock = FIRST50;
                break;
            }
            case 3: {
                distanceLock = FIRST75;
                break;
            }

        }
        // time when first packet was received. -1 if we never received one
        packetReceivedAt = -1;
        // the random timeout that was chosen from window. Is 10 when timeout has been canceled.
        timeoutChosen = 10;
        EV << "Initializing " << par("appName").stringValue() << std::endl;
    }
    else if (stage == 1) {
        // Initializing members that require initialized other modules goes here
        if (getParentModule()->getIndex() == 0) {
            scheduleAt(start, sendLeaderEvt);
        }
    }
}

void MyVeinsApp::finish()
{
    DemoBaseApplLayer::finish();
    recordScalar("packetsReceived", msgIDs.size());
    recordScalar("packetReceivedAt", packetReceivedAt);
    recordScalar("timeoutChosen", timeoutChosen);
    recordScalar("hopCount", hopCount);
    recordScalar("msgID", msgID);
    // statistics recording goes here
}

void MyVeinsApp::onBSM(DemoSafetyMessage* bsm)
{
    // Your application has received a beacon message from another car or RSU
    // code for handling the message goes here
}

void MyVeinsApp::onWSM(BaseFrame1609_4* frame)
{
    hopCount++;
    // Your application has received a data message from another car or RSU
    // code for handling the message goes here, see TraciDemo11p.cc for examples
    /*
    TraCIDemo11pMessage* wsm = check_and_cast<TraCIDemo11pMessage*>(frame);

    if (scheduledMsg != nullptr && scheduledMsg->isScheduled()) {
        // we got a message while in timeout. Cancel it
        // if we cancel timeout we return timeoutChosen to default value so we know it didnt get through
        timeoutChosen = 10;
        cancelAndDelete(scheduledMsg);
        //scheduledMsg has to be nullptr now to avoid dangling pointer issues.
        scheduledMsg = nullptr;
        findHost()->getDisplayString().setTagArg("i", 1, "green");
   } else {
       // if we already had the packet ignore it
       int tmp = wsm->getMsgID();
       if (msgIDs.count(tmp) == 1) {
           return;
       }
       // first time receiving packet going in timeout
       msgIDs.insert(tmp);
       packetReceivedAt = simTime();
       //schedule message after a timeout
       scheduledMsg = wsm->dup();
       findHost()->getDisplayString().setTagArg("i", 1, "blue");
       //how to modify our chosen timeout
       switch (timeoutType) {
           case NOMOD: {
               timeoutChosen = uniform(timeoutMin , timeoutMax);
               break;
           }
           case DISTANCE: {
               //im not sure if curPosition variables always works for this so im using this method
               auto mobility = TraCIMobilityAccess().get(getParentModule());
               Coord myPos = mobility->getPositionAt(simTime());
               double distance = myPos.distance(wsm->getLastSenderPos());
               double factor;
               simtime_t timeoutMinFactored = timeoutMin;
               //EV << "The distance is: " << distance;
               factor = distance / scalingDistance; // With simplepathloss its around 575 of effective transmission range. With nakagami probability id increase the 0 second timeout to 650
               if (distance>scalingDistance) {
                   factor = 1;
               }
               switch (distanceLock) {
                case NOMODIFICATION:
                    break;
                case FIRST25:
                    if (distance<=(0.25*scalingDistance)) {
                        timeoutMinFactored = 0.75*timeoutMax;

                    }
                    break;
                case FIRST50:
                    if (distance<=(0.5*scalingDistance)) {
                        timeoutMinFactored = 0.5*timeoutMax;

                    }
                    break;
                case FIRST75:
                    if (distance<=(0.75*scalingDistance)) {
                        timeoutMinFactored = 0.25*timeoutMax;

                    }
                    break;
                default:
                    break;
               }
               simtime_t timeoutMaxFactored = timeoutMax*(1-factor);
               timeoutChosen = uniform(timeoutMinFactored , timeoutMaxFactored);
               //timeoutChosen = timeoutMax*(1-factor);
               break;
           }
           case SIGNALPOWER: {
               // getting signal power is a bit rough. Have to go through control info to get to the decider.
               simtime_t timeoutMinFactored = timeoutMin;
               simtime_t timeoutMaxFactored = timeoutMax;
               if (cObject* ctrlInfo = wsm->getControlInfo()) {
                   if (PhyToMacControlInfo* phyCtrlInfo = dynamic_cast<PhyToMacControlInfo*>(ctrlInfo)) {
                       DeciderResult80211* result = dynamic_cast<DeciderResult80211*>(phyCtrlInfo->getDeciderResult());
                       if (result) {
                           //because of the heavy fluctuations and similar signal powers at 200+ distances i decided to make the timeoutscaling begin at -85
                           double recvPower_dBm = result->getRecvPower_dBm();
                           if (recvPower_dBm<-92.5) {
                              timeoutChosen = 0;
                              break;
                           }

                           if (recvPower_dBm>-88.1) {
                              timeoutMinFactored = timeoutMax*0.5;
                           }
                           else {
                               if (recvPower_dBm>-90.3) {
                                   timeoutMinFactored = timeoutMax*0.5;
                               }
                               double factor = (-88.1 - recvPower_dBm) / (-88.1 - -92.5);
                               timeoutMaxFactored = timeoutMaxFactored*(1-factor);
                           }
                           timeoutChosen = uniform(timeoutMinFactored, timeoutMaxFactored);
                       }
                   }
               }
              break;
           }

       }
       scheduleAt(simTime() + timeoutChosen, scheduledMsg);
   }
   */

}

void MyVeinsApp::onWSA(DemoServiceAdvertisment* wsa)
{
    // Your application has received a service advertisement from another car or RSU
    // code for handling the message goes here, see TraciDemo11p.cc for examples
}

void MyVeinsApp::handleSelfMsg(cMessage* msg)
{
    // this method is for self messages (mostly timers)
    // it is important to call the DemoBaseApplLayer function for BSM and WSM transmission

    if (TraCIDemo11pMessage* wsm = dynamic_cast<TraCIDemo11pMessage*>(msg)) {
            //we get here after our non canceled timeout. Sending message.
            scheduledMsg = nullptr;
            findHost()->getDisplayString().setTagArg("i", 1, "yellow");
            hopCount = wsm->getHopCount();
            hopCount++;
            TraCIDemo11pMessage* wsmDup = wsm->dup();
            wsmDup->setHopCount(hopCount);
            populateWSM(wsmDup);
            if (timeoutType==DISTANCE) {
                auto mobility = TraCIMobilityAccess().get(getParentModule());
                Coord myPos = mobility->getPositionAt(simTime());
                wsmDup->setLastSenderPos(myPos);
            }
            sendDown(wsmDup);
            delete wsm;
            return;
    }
    switch (msg->getKind()) {
        // Its a leader msg. Start broadcasting a new message and schedule next one.
        case SEND_LEADER_EVT: {
            findHost()->getDisplayString().setTagArg("i", 1, "yellow");
            msgIDs.insert(msgID);
            TraCIDemo11pMessage* wsm = new TraCIDemo11pMessage();
            populateWSM(wsm);
            wsm->setHopCount(0);
            wsm->setMsgID(msgID);
            if (timeoutType==DISTANCE) {
                auto mobility = TraCIMobilityAccess().get(getParentModule());
                Coord myPos = mobility->getPositionAt(simTime());
                wsm->setLastSenderPos(myPos);
            }
            msgID++;
            sendDown(wsm);
            findHost()->getDisplayString().setTagArg("i", 1, "red");
            // to enable intervall msging add the following line
            scheduleAt(simTime() + interval, sendLeaderEvt);
            break;
        }
        // Not used at the moment
        case SEND_TIMEOUT_EVT: {
            // just for the offchance code arrives here
            DemoBaseApplLayer::handleSelfMsg(msg);
            break;
        }

        default: {
            DemoBaseApplLayer::handleSelfMsg(msg);
        }
        }
}

void MyVeinsApp::handlePositionUpdate(cObject* obj)
{
    DemoBaseApplLayer::handlePositionUpdate(obj);
    // the vehicle has moved. Code that reacts to new positions goes here.
    // member variables such as currentPosition and currentSpeed are updated in the parent class
    // stopped for for at least 10s?T
}

