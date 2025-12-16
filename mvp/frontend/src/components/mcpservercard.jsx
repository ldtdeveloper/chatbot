import React from 'react';
import '../assets/mcpservercard.css';
import { IoCloseOutline } from "react-icons/io5";
import Switch from '@mui/material/Switch';
import Tooltip from "@mui/material/Tooltip";
import { useState,useEffect } from 'react'
import HubSpotForm from '../components/mcpserver'
import {integrationConfigService} from '../services/services'
import { use } from 'react';
import { toast } from "sonner";

export default function AppIconsCard({setShowMcpServerCard,setChecked,selectedAgent}) {
    const [checked, setCheckedLocal] = useState(false);
    const [showHubSpotForm, setShowHubSpotForm] = useState(false);
    const [hubspotformdata, setHubSpotFormData] = useState(null)
    const [configId, setConfigId] = useState(null);
    useEffect(() => {
      async function fetchData() {
        try {
          if (selectedAgent) {
            const response = await integrationConfigService.list(selectedAgent.id);
            setConfigId(response[0].id);
            setCheckedLocal(response[0].is_active);
            setHubSpotFormData(response);
            console.log("Use effect hit")
          }
        } catch (error) {
          console.error("Error fetching agent data:", error);
        }
      }

  fetchData();
}, [checked]); 

    
    const handleClick = async () => {
      try{
        setShowHubSpotForm(true);
      }
      catch(error){
      }
  };

  const handleCancel = () => {
    setShowMcpServerCard(false);
  }

   const handleChange = async (e) => {    
    try{
      if (configId){
          const response = await integrationConfigService.update(configId, {agent_id: selectedAgent.id,is_active: e.target.checked});
          setCheckedLocal(response.is_active);
          setShowHubSpotForm(false);
          toast.success("Configuration saved successfully.");
      }
      else{
        setShowHubSpotForm(true);
      }
    }
    catch(error){
        toast.error("Something went wrong while disabling the integration." + error);
      }
    }

  return (
    <div className= "app-container" id ="mcpservercard">
      <div className="app-card" >    
        <div className="modal-box">
        <IoCloseOutline className="close-icon" onClick={handleCancel} />
        </div>
        <div className="apps-grid">
          <div className="app-item">
            <div className="app-icon bg-green">
                <img src="/hubspot.svg" alt="icon" style={{ width: "100%", height: "100%", objectFit: "contain" }} onClick={handleClick}/>
            </div>
            <Tooltip title="MCP server">
            <Switch
                size= "small"
                checked={checked}
                onChange={handleChange}
                slotProps={{ input: { 'aria-label': 'controlled' } }}
              />
            </Tooltip>
          </div>
        </div>
      </div>
        {showHubSpotForm && <HubSpotForm setShowHubSpotForm = {setShowHubSpotForm} setCheckedLocal = {setCheckedLocal} selectedAgent = {selectedAgent} hubspotformdata = {hubspotformdata}/>}
    </div>  );
}