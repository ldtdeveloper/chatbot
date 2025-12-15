import { useState } from 'react';
import '../assets/mcpserver.css';
import {integrationConfigService} from '../services/services'
import { IoCloseOutline } from "react-icons/io5";
import { toast } from "sonner";


export default function HubSpotForm({ setShowHubSpotForm,setCheckedLocal,selectedAgent,hubspotformdata }) {
  const [intialformdata, setIntialFormData] = useState(() => {
    if (hubspotformdata && hubspotformdata.length > 0) {
      console.log("Decrypted Key " + hubspotformdata[0].masked_key)
      return {
        instructions: hubspotformdata[0].instructions || '',
        hubspotKey: hubspotformdata[0].masked_key || ''
      };
    }
    return {
      instructions: '',
      hubspotKey: ''
    };
  });
  const [formData, setFormData] = useState(intialformdata);

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
      let response; ;
      const payload = {
        instructions: formData.instructions
      }
      if(hubspotformdata && hubspotformdata.length > 0){
        response = await integrationConfigService.update(hubspotformdata[0].id,payload);
      }
      else{
        payload.encrypted_key = formData.hubspotKey,
        payload.agent_id = selectedAgent.id,
        payload.provider = "hubspot"
        response = await integrationConfigService.create(payload);
      }
      console.log(response.success)
      toast.success("Configuration saved successfully.");
      setShowHubSpotForm(false);
      setCheckedLocal(true);
    } catch (error) {
        setShowHubSpotForm(false);
        setCheckedLocal(false);
        toast.error("Something went wrong")
    }
  };

  const handleCancel = () => {
    setShowHubSpotForm(false);
  }

  return (
    <div className="container">
      <div className="form-card">
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