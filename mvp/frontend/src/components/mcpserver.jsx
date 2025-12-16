import { useState, useEffect } from 'react';
import '../assets/mcpserver.css';
import {integrationConfigService} from '../services/services'
import { IoCloseOutline } from "react-icons/io5";
import { toast } from "sonner";


export default function HubSpotForm({ setShowHubSpotForm,setCheckedLocal,selectedAgent,hubspotformdata,onSuccess }) {
  const [formData, setFormData] = useState({
    instructions: '',
    hubspotKey: ''
  });

  // Update form data when hubspotformdata changes or when form opens
  useEffect(() => {
    console.log("HubSpotForm useEffect triggered, hubspotformdata:", hubspotformdata);
    if (hubspotformdata && hubspotformdata.length > 0) {
      console.log("Setting form data with:", {
        instructions: hubspotformdata[0].instructions,
        masked_key: hubspotformdata[0].masked_key
      });
      setFormData({
        instructions: hubspotformdata[0].instructions || '',
        hubspotKey: hubspotformdata[0].masked_key || ''
      });
    } else {
      console.log("No hubspotformdata, setting empty form");
      setFormData({
        instructions: '',
        hubspotKey: ''
      });
    }
  }, [hubspotformdata]);

  // Don't render if no agent is selected - check after all hooks
  if (!selectedAgent || !selectedAgent.id) {
    return null;
  }

  const handleChange = (e) => {
    console.log(e.target.value);
    const name = e.target.name;
    const value = e.target.value;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try{
      if (!selectedAgent || !selectedAgent.id) {
        toast.error("No agent selected");
        return;
      }
      let response; ;
      const payload = {
        instructions: formData.instructions
      }
      if(hubspotformdata && hubspotformdata.length > 0){
        response = await integrationConfigService.update(hubspotformdata[0].id,payload);
      }
      else{
        if (!formData.hubspotKey) {
          toast.error("HubSpot API key is required");
          return;
        }
        payload.encrypted_key = formData.hubspotKey,
        payload.agent_id = selectedAgent.id,
        payload.provider = "hubspot"
        response = await integrationConfigService.create(payload);
      }
      console.log(response.success)
      toast.success("Configuration saved successfully.");
      setShowHubSpotForm(false);
      setCheckedLocal(true);
      // Refetch data to get updated configId and data
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
        setShowHubSpotForm(false);
        setCheckedLocal(false);
        toast.error("Something went wrong: " + (error.message || error))
    }
  };

  const handleCancel = () => {
    setShowHubSpotForm(false);
  }

  return (
    <div className="container" onClick={(e) => e.stopPropagation()}>
      <div className="form-card" onClick={(e) => e.stopPropagation()}>
        <h2 className="form-title">Configuration</h2>
        
        <div className="form-content">
            <div className="modal-box">
            <IoCloseOutline className="close-icon" onClick={handleCancel} />
            </div>
          <div className="form-group">
            <label htmlFor="instructions" className="form-label">
              Instructions
            </label>
            <textarea
              id="instructions"
              name="instructions"
              value={formData.instructions}
              onChange={handleChange}
              rows="4"
              className="form-textarea"
              placeholder="Enter your instructions here..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="hubspotKey" className="form-label">
              HubSpot Key
            </label>
            <input
              type={hubspotformdata ? "text" : "password"}
              id="hubspotKey"
              name="hubspotKey"
              value={formData.hubspotKey}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your HubSpot API key..."
            />
          </div>
          <div className='button-row'>
          <button onClick={handleSubmit} className="submit-button">
            Submit
          </button>
          <button className="cancel-button" onClick={handleCancel}>
            Cancel
          </button>
          </div>
        </div>
      </div>
    </div>
  );
}