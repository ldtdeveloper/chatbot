import React,{useState} from "react";
import { useQuery} from "@tanstack/react-query";
import { planService} from "../services/services";
import '../styles/Plans.css';
import ViewPlan from '../components/ViewPlan'
import PlanForm from "../components/PlanForm";
import { showError,showSuccess } from "../utils/toast";
import { FaEye, FaEdit, FaTrash, FaToggleOn, FaToggleOff } from 'react-icons/fa';

// Currency symbols mapping
const getCurrencySymbol = (currency) => {
  const currencyMap = {
    'USD': '$',
    'INR': '₹',
    'BHD': 'BD',
    'KWD': 'KD',
    'OMR': 'OMR',
    'SAR': 'SAR',
    'AED': 'AED',
    'EUR': '€',
    'GBP': '£',
  };
  return currencyMap[currency] || currency || '$';
};

// Currency flag emojis (optional, for visual appeal)
const getCurrencyFlag = (currency) => {
  const flagMap = {
    'USD': '🇺🇸',
    'INR': '🇮🇳',
    'BHD': '🇧🇭',
    'KWD': '🇰🇼',
    'OMR': '🇴🇲',
    'SAR': '🇸🇦',
    'AED': '🇦🇪',
    'EUR': '🇪🇺',
    'GBP': '🇬🇧',
  };
  return flagMap[currency] || '💵';
};

export default function Plans() {
      const [showPlanDetail, setPlanDetail] = useState(false)
      const [selectedPlan, setSelectedPlan] = useState()
      const [showPlanForm, setPlanForm]  = useState(false)
      const { data: plans, isLoading ,refetch} = useQuery({
        queryKey: ['plans'],
        queryFn: planService.listPlan,
      })
      console.log(plans)
      const handleViewPlan = (plan) => {
            console.log(`View plan clicked ${plan}`)
            setSelectedPlan(plan);
            setPlanDetail(true);
            console.log(`Selected plan ${selectedPlan}`)
        };

      const handleEditPlan = (plan) => {
            console.log(`Handle Edit button ..........${plan}`)
            setSelectedPlan(plan);
            setPlanForm(true);
      }

       const handleSubmit = async (submitData,initialData) => {
        setPlanForm(false);
        setSelectedPlan(null)
        let response = null
        try{
            if(initialData==null){
                response = await planService.createPlans(submitData)
                if(response?.id){
                    refetch()
                    showSuccess("Plan created successfully")
                    return
                }
                showError("Plan not created")
            }
            else{
                response = await planService.updatePlan(submitData.id,submitData)
                if(response?.id){
                    refetch()
                    showSuccess("Plan updated successfully")
                    return 
                }
                showError("Plan not updated")
            }
        }
        catch(err) {
            console.log(err)
            showError(err.message)
        }
      }

      const handleBack = () =>{
        setSelectedPlan(false);
        setPlanForm(false);
      }

      const handleIsActive= async (id,isActive) =>{
        try{
            const response = await planService.updatePlan(id,{"is_active": isActive})
            if(response?.id){
                refetch()
                if(isActive){
                    showSuccess("Plan activated")
                }
                else{
                    showSuccess("Plan deactivated")
                }
                return
            }
        }
        catch(err){
            showError(err.message)
        }
      }
      
      const handleDelete = async (id) => {
        try{
            const response = await planService.deletePlan(id)
            if(response.message!=""){
                refetch()
                showSuccess("Plan deleted successfully")
                return
            }
        }
        catch(err){
            showError(err.message)
        }
      }

      if (isLoading) return <div>Loading...</div>
    
      const planList = Array.isArray(plans) ? plans : [];
    return (
        <div className="plans">

            <div className="page-header">
            <h1>Plan Management</h1>
            <button onClick={() => setPlanForm(true)}>
            +  Add new plan
           </button>
            </div>
            <div className="plans-list">
            {planList.length!=0 && planList.map((plan) => {
              const currency = plan.currency || 'USD';
              const currencySymbol = getCurrencySymbol(currency);
              const walletCredits = plan.wallet_credits || plan.credits || 0;
              const planType = plan.plan_type || 'monthly';
              
              return (
                <div key={plan.id} className="plan-card">
                <div className="plan-info">
                    <h3>{plan.name}</h3>
                    
                    {plan.description && (
                      <p className="plan-description">
                        {plan.description}
                      </p>
                    )}

                    <div className="plan-meta">
                    <span className="plan-price">
                        <span className="currency-symbol">{currencySymbol}</span>
                        <span className="price-amount">{plan.price}</span>
                        <span className="plan-type-badge">{planType}</span>
                    </span>
                    </div>
                </div>

                <div className="plan-actions">
                    <button
                    className="action-btn view-btn" 
                    onClick={() => handleViewPlan(plan)}
                    title="View Plan">
                    <FaEye />
                    </button>

                    <button 
                    className="action-btn edit-btn" 
                    onClick={() => handleEditPlan(plan)}
                    title="Edit Plan">
                    <FaEdit />
                    </button>

                    <button 
                    className="action-btn edit-btn"
                    onClick={() => handleIsActive(plan.id, !plan.is_active)}
                    title={plan.is_active ? "Deactivate Plan" : "Activate Plan"}
                >
                  {plan.is_active ? <FaToggleOn /> : <FaToggleOff />}
                </button>

                    <button 
                    className="action-btn delete-btn" 
                    onClick={()=> handleDelete(plan.id)}
                    title="Delete Plan">
                    <FaTrash />
                    </button>
                </div>
                </div>
              );
            })}
            {planList.length === 0 && <p>No plans found.</p>}
            </div>
            {showPlanDetail && selectedPlan && (
                <div className="modal-overlay" onClick={() => setPlanDetail(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                    <ViewPlan plan={selectedPlan} onBack={() => setPlanDetail(false) } />
                    </div>
                </div>
                )}
            {showPlanForm  && <PlanForm initialData = {selectedPlan? selectedPlan : null} onSubmit={handleSubmit} onBack={handleBack}/>}
        </div>
        )
}
