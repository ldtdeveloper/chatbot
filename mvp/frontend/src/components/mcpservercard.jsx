import React from 'react';
import '../assets/mcpservercard.css';
import { IoCloseOutline } from "react-icons/io5";
import Switch from '@mui/material/Switch';
import Tooltip from "@mui/material/Tooltip";
import { useState,useEffect,useRef } from 'react'
import HubSpotForm from '../components/mcpserver'
import {integrationConfigService} from '../services/services'
import Toastify from "toastify-js";
import "toastify-js/src/toastify.css";

export default function AppIconsCard({setShowMcpServerCard,setChecked,selectedAgent}) {
    const [checked, setCheckedLocal] = useState(false);
    const [showHubSpotForm, setShowHubSpotForm] = useState(false);
    const [hubspotformdata, setHubSpotFormData] = useState(null)
    const [configId, setConfigId] = useState(null);
    const [formKey, setFormKey] = useState(0); // Key to force form remount
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

    // Function to refetch data (can be called after form submission)
    const refetchData = async () => {
      try {
        if (selectedAgent && selectedAgent.id) {
          const response = await integrationConfigService.list(selectedAgent.id);
          if (response && response.length > 0) {
            setConfigId(response[0].id);
            setCheckedLocal(Boolean(response[0].is_active));
            setHubSpotFormData(response);
          } else {
            setConfigId(null);
            setCheckedLocal(false);
            setHubSpotFormData(null);
          }
        }
      } catch (error) {
        console.error("Error refetching agent data:", error);
      }
    }; 

    
    const handleClick = async (e) => {
      // Stop event propagation to prevent closing
      if (e) {
        e.stopPropagation();
        e.preventDefault();
      }
      try{
        // If data exists, fetch fresh data from API before showing form
        if (configId && selectedAgent?.id) {
          const response = await integrationConfigService.list(selectedAgent.id);
          if (response && response.length > 0) {
            // Set the data first
            setHubSpotFormData(response);
            // Update form key to force remount with new data
            setFormKey(prev => prev + 1);
            console.log("Fetched fresh data for form:", response);
            // Use requestAnimationFrame to ensure state is updated before opening form
            requestAnimationFrame(() => {
              setTimeout(() => {
                setShowHubSpotForm(true);
              }, 50);
            });
          } else {
            // No data found, open empty form
            setHubSpotFormData(null);
            setShowHubSpotForm(true);
          }
        } else {
          // No configId, open empty form for new configuration
          setHubSpotFormData(null);
          setShowHubSpotForm(true);
        }
      }
      catch(error){
        console.error("Error opening HubSpot form:", error);
        Toastify({
          text: `Failed to load configuration data`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#dc2626",
          style: {
              borderRadius: "10px",
              width: "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
        // Still open form even if fetch fails, but with existing data if available
        setShowHubSpotForm(true);
      }
  };

  const handleCancel = () => {
    setShowMcpServerCard(false);
  }

   const handleChange = async (e) => {    
    // Capture previous state before any changes for error handling
    const previousCheckedState = checked;
    const newCheckedState = Boolean(e.target.checked);
    
    // Stop event propagation
    if (e) {
      e.stopPropagation();
    }
    
    try{
      if (!selectedAgent || !selectedAgent.id) {
        Toastify({
          text: `No agent selected`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#dc2626",
          style: {
              borderRadius: "10px",
              width: "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
        return;
      }
      
      if (configId){
          // Data exists: Just update the toggle state (is_active) in DB
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
          // Don't open/close form, just update toggle state
          Toastify({
          text: newCheckedState ? "Integration activated" : "Integration deactivated",
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#16a34a",
          style: {
              borderRadius: "10px",
              width: "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
      }
      else{
        // No data exists: Open form to create new configuration
        setShowHubSpotForm(true);
      }
    }
    catch(error){
        // Revert the optimistic update on error
        setCheckedLocal(previousCheckedState);
        Toastify({
          text: `Something went wrong while updating the integration: ${error.message || error}`,
          duration: 2000,
          gravity: "top",
          position: "center",
          backgroundColor: "#dc2626",
          style: {
              borderRadius: "10px",
              width: "350px",       // set your desired width
              textAlign: "left"   // optional, centers the text
          }
      }).showToast();
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
        {showHubSpotForm && <HubSpotForm key={`${configId || 'new'}-${formKey}`} setShowHubSpotForm = {setShowHubSpotForm} setCheckedLocal = {setCheckedLocal} selectedAgent = {selectedAgent} hubspotformdata = {hubspotformdata} onSuccess = {refetchData}/>}
    </div>  );
}