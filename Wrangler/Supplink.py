# SFCTA NetworkWrangler: Wrangles transit and road networks from SF-CHAMP
# Copyright (C) 2018 San Francisco County Transportation Authority
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .NetworkException import NetworkException

__all__ = ['Supplink']

class Supplink(dict):
    """ PNR Support Link.
       'node' property is the node-pair for this link (e.g. 24133-34133)
       'comment' is any end-of-line comment for this link including the leading semicolon
        All other attributes are stored in a dictionary (e.g. thislink['MODE']='1,2')
    """
    MODES = {1:"WALK_ACCESS",
             2:"WALK_EGRESS",
             3:"DRIVE_ACCESS",
             4:"DRIVE_EGRESS",
             5:"TRANSIT_TRANSFER",
             6:"DRIVE_FUNNEL",
             7:"WALK_FUNNEL"}
    MODES_INV = dict((v,k) for k,v in MODES.iteritems())
    
    def __init__(self):
        dict.__init__(self)
        self.id=''  # string, e.g. "1-7719"
        self.comment=None
        
        # components of ID, ints
        self.Anode = None
        self.Bnode = None
        self.mode  = None

    def __repr__(self):
        s = "SUPPLINK N=%5d-%5d " % (self.Anode,self.Bnode)

        # Deal w/all link attributes
        fields = []
        for k in sorted(self.keys()):
            fields.append('%s=%s' % (k,self[k]))

        s += " ".join(fields)
        if self.comment:
            s = "%-80s %s" % (s, self.comment)

        return s

    def setId(self, id):
        self.id = id
        
        nodeList=self.id.split('-')
        self.Anode = int(nodeList[0])
        self.Bnode = int(nodeList[1])
        
    def setMode(self, newmode=None):
        """
        If newmode is passed, then uses that.
        Otherwise, figure out the mode from the text in the dictionary.
        """
        if newmode==None and self.mode: return
        
        # find it in my dictionary
        for k,v in self.items():
            if k.lower() == "mode":
                if newmode:
                    self.mode = newmode
                    self[k] = str(self.mode)
                else:
                    self.mode = int(v)
        
        # it wasn't in the dictionary
        if newmode and not self.mode:
            self.mode = newmode
            self["MODE"] = str(self.mode)
        
        if not self.mode:
            raise NetworkException("Supplink mode not set: " + str(self))

    def isWalkAccess(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="WALK_ACCESS")
    
    def isWalkEgress(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="WALK_EGRESS")
    
    def isDriveAccess(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="DRIVE_ACCESS")

    def isDriveEgress(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="DRIVE_EGRESS")

    def isTransitTransfer(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="TRANSIT_TRANSFER")
    
    def isWalkFunnel(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="WALK_FUNNEL")

    def isDriveFunnel(self):
        self.setMode()
        return (Supplink.MODES[self.mode]=="DRIVE_FUNNEL")
    
    def isOneWay(self):
        for k,v in self.items():
            if k.upper() == "ONEWAY": return v.upper() in ["Y", "YES", "1", "T", "TRUE"]
        # Cube says default is False
        return False
    
    def reverse(self):
        # not one-way; nothing to do
        if not self.isOneWay(): return
        
        temp = self.Anode
        self.Anode = self.Bnode
        self.Bnode = temp
        
        self.id = "%d-%d" % (self.Anode, self.Bnode)
        if   self.isWalkAccess(): self.setMode(Supplink.MODES_INV["WALK_EGRESS"])
        elif self.isWalkEgress(): self.setMode(Supplink.MODES_INV["WALK_ACCESS"])
        elif self.isDriveAccess(): self.setMode(Supplink.MODES_INV["DRIVE_EGRESS"])
        elif self.isDriveEgress(): self.setMode(Supplink.MODES_INV["DRIVE_ACCESS"])