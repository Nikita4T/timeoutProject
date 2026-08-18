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
// Modified by Nikita Hess, 2026.
// Extended for contention-based forwarding and timeout-based
// message dissemination experiments.
// See Git history for detailed changes.

package org.car2x.veins.modules.application.traci;
import org.car2x.veins.modules.application.ieee80211p.DemoBaseApplLayer;

//
// network description file for your Veins Application. Add parameters here
//
simple MyVeinsApp extends DemoBaseApplLayer
{
    parameters:
        @class(veins::MyVeinsApp);
        string appName = default("Timeout Project");
        double start @unit(s);
        double interval @unit(s);
        double timeoutMin @unit(s);
        double timeoutMax @unit(s);
        double scalingDistance; // for distance based: scaling distance based on this distance.
        int timeoutType; // cant declare enums here so 0 for NOMOD, 1 for DISTANCE, 2 for SIGNALPOWER
        int distanceLock; // for distance based: makes timeoutmin bigger so later percent of vehicles are forced as relays if they are reached 0=NOMOD 1=FIRST25 2=FIRST50 3=FIRST75
}
