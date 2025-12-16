import React from 'react';
import '../assets/mcpservercard.css';
import { IoCloseOutline } from "react-icons/io5";
import Switch from '@mui/material/Switch';
import Tooltip from "@mui/material/Tooltip";
import { useState,useEffect,useRef } from 'react'
import HubSpotForm from '../components/mcpserver'
import {integrationConfigService} from '../services/services'
import { toast } from "sonner";

export default function AppIconsCard({setShowMcpServerCard,setChecked,selectedAgent}) {
    const [checked, setCheckedLocal] = useState(false);
    const [showHubSpotForm, setShowHubSpotForm] = useState(false);
    const [hubspotformdata, setHubSpotFormData] = useState(null)
    const [configId, setConfigId] = useState(null);
    const previousAgentIdRef = useRef(null);
    
    useEffect(() => {
      const currentAgentId = selectedAgent?.id;
      
      // Only reset form visibility when agent actually changes (not on every render)
      if (previousAgentIdRef.current !== null && previousAgentIdRef.current !== currentAgentId) {
        setShowHubSpotForm(false);
      }
      previousAgentIdRef.current = currentAgentId;
      
      // Reset state when selectedAgent changes
      setCheckedLocal(false);
      setConfigId(null);
      setHubSpotFormData(null);
      
      async function fetchData() {
        try {
          if (selectedAgent && selectedAgent.id) {
            const response = await integrationConfigService.list(selectedAgent.id);
            if (response && response.length > 0) {
              setConfigId(response[0].id);
              // Ensure is_active is always a boolean
              setCheckedLocal(Boolean(response[0].is_active));
              setHubSpotFormData(response);
              console.log("Use effect hit")
            } else {
              setConfigId(null);
              setCheckedLocal(false);
              setHubSpotFormData(null);
            }
          }
        } catch (error) {
          console.error("Error fetching agent data:", error);
          setConfigId(null);
          setCheckedLocal(false);
          setHubSpotFormData(null);
        }
      }

  fetchData();
}, [selectedAgent?.id]); // Only depend on the ID, not the whole object 

    
    const handleClick = (e) => {
      // Stop event propagation to prevent closing
      if (e) {
        e.stopPropagation();
        e.preventDefault();
      }
      try{
        console.log("Opening HubSpot form, current data:", hubspotformdata);
        setShowHubSpotForm(true);
      }
      catch(error){
        console.error("Error opening HubSpot form:", error);
      }
  };

  const handleCancel = () => {
    setShowMcpServerCard(false);
  }

   const handleChange = async (e) => {    
    // Capture previous state before any changes for error handling
    const previousCheckedState = checked;
    const newCheckedState = Boolean(e.target.checked);
    
    try{
      if (!selectedAgent || !selectedAgent.id) {
        toast.error("No agent selected");
        return;
      }
      
      if (configId){
          // Optimistically update the UI immediately
          setCheckedLocal(newCheckedState);
          
          const response = await integrationConfigService.update(configId, {
            agent_id: selectedAgent.id,
            is_active: newCheckedState
          });
          
          // Update from response to ensure sync with backend
          // Handle different possible response structures
          const isActive = response?.is_active ?? response?.data?.is_active ?? newCheckedState;
          setCheckedLocal(Boolean(isActive));
          setShowHubSpotForm(false);
          toast.success("Configuration saved successfully.");
      }
      else{
        setShowHubSpotForm(true);
      }
    }
    catch(error){
        // Revert the optimistic update on error
        setCheckedLocal(previousCheckedState);
        toast.error("Something went wrong while updating the integration: " + (error.message || error));
      }
    }

  // Don't render if no agent is selected - check after all hooks
  if (!selectedAgent || !selectedAgent.id) {
    return null;
  }

  return (
    <div className= "app-container" id ="mcpservercard">
      <div className="app-card" >    
        <div className="modal-box">
        <IoCloseOutline className="close-icon" onClick={handleCancel} />
        </div>
        <div className="apps-grid">
          <div className="app-item" onClick={(e) => e.stopPropagation()}>
            <div className="app-icon bg-green" onClick={(e) => e.stopPropagation()}>
                <img src="/hubspot.svg" alt="icon" style={{ width: "100%", height: "100%", objectFit: "contain", cursor: "pointer" }} onClick={handleClick}/>
            </div>
            <Tooltip title="MCP server">
            <Switch
                size= "small"
                checked={Boolean(checked)}
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